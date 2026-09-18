"""Auditorías de solo lectura sobre entidades propias de COpenMed.

Cada función devuelve una lista de "hallazgos" (dicts) para que el usuario
confirme antes de aplicar ninguna corrección real — el nivel de autonomía
por defecto (ver docs/copenmed/README.md) es "auditar y listar primero".
Ninguna función de este módulo escribe en la API.

Las reglas R1-R10 (correcciones estructurales) están documentadas en
docs/copenmed/PLAYBOOK.md sección 5; las reglas R11-R16 (política de
creación/calidad de entidades, 2026-09-18) en la sección 6 del mismo archivo.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def contar_asociaciones(client, ids_entidad: list[int]) -> dict[int, int]:
    """Regla R1: conteo fiable de asociaciones por entidad."""
    return {i: client.contar_asociaciones_propias(i) for i in ids_entidad}


def detectar_disease_con_hijos(client, ids_entidad: list[int]) -> list[dict[str, Any]]:
    """Regla R2: Disease que en realidad debería ser GroupOfDiseases."""
    hallazgos = []
    for id_entidad in ids_entidad:
        entrantes = client.buscar_asociaciones(id_entidad2=id_entidad, page_size=200)
        hijos = [a for a in entrantes["data"] if a.get("TipoAsociacion") == "Disease belongs to Group"]
        if hijos:
            hallazgos.append(
                {
                    "regla": "R2",
                    "id_entidad": id_entidad,
                    "mensaje": "Tiene hijos vía 'Disease belongs to Group'; revisar si debería ser GroupOfDiseases.",
                    "hijos": [a["IdEntidad1"] for a in hijos],
                }
            )
    return hallazgos


def detectar_pares_multiples(client, ids_entidad: list[int], id_estudiante: int | None = None) -> list[dict[str, Any]]:
    """Reglas R3/R8: mismo par de entidades con más de una asociación propia (ciclo o duplicado)."""
    id_estudiante = id_estudiante or client.id_estudiante
    por_par: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for id_entidad in ids_entidad:
        for kwargs in ({"id_entidad1": id_entidad}, {"id_entidad2": id_entidad}):
            resp = client.buscar_asociaciones(id_estudiante=id_estudiante, page_size=200, **kwargs)
            for a in resp["data"]:
                par = tuple(sorted((a["IdEntidad1"], a["IdEntidad2"])))
                por_par[par].append(a)
    hallazgos = []
    for par, asociaciones in por_par.items():
        vistos = {a["IdAsociacion"]: a for a in asociaciones}
        if len(vistos) > 1:
            tipos = {a["TipoAsociacion"] for a in vistos.values()}
            hallazgos.append(
                {
                    "regla": "R8" if len(tipos) == 1 else "R3",
                    "par": par,
                    "mensaje": (
                        "Mismo par con >1 asociación propia y mismo tipo: duplicado exacto."
                        if len(tipos) == 1
                        else "Mismo par con >1 asociación propia y tipos distintos: revisar manualmente (posible ciclo lógico)."
                    ),
                    "ids_asociacion": list(vistos.keys()),
                    "tipos": list(tipos),
                }
            )
    return hallazgos


def detectar_causalidad_invertida(client, ids_entidad: list[int], id_estudiante: int | None = None) -> list[dict[str, Any]]:
    """Regla R4: 'Disease/Group may cause Cause' casi siempre está invertida."""
    id_estudiante = id_estudiante or client.id_estudiante
    hallazgos = []
    for id_entidad in ids_entidad:
        resp = client.buscar_asociaciones(id_entidad1=id_entidad, id_estudiante=id_estudiante, page_size=200)
        for a in resp["data"]:
            if a.get("TipoAsociacion") in ("Disease may cause Cause", "Group may cause Cause"):
                hallazgos.append(
                    {
                        "regla": "R4",
                        "id_asociacion": a["IdAsociacion"],
                        "mensaje": (
                            "Tipo casi siempre invertido; revisar si debería ser "
                            "'Cause may cause Disease' (62) con IdEntidad1/IdEntidad2 intercambiados."
                        ),
                        "asociacion": a,
                    }
                )
    return hallazgos


def detectar_asociaciones_sin_descripcion(client, ids_entidad: list[int], id_estudiante: int | None = None) -> list[dict[str, Any]]:
    """Regla R10: asociaciones sin Descripcion son candidatas a revisión manual con criterio clínico."""
    id_estudiante = id_estudiante or client.id_estudiante
    hallazgos = []
    for id_entidad in ids_entidad:
        resp = client.buscar_asociaciones(id_entidad1=id_entidad, id_estudiante=id_estudiante, page_size=200)
        for a in resp["data"]:
            if not a.get("Descripcion"):
                hallazgos.append(
                    {
                        "regla": "R10",
                        "id_asociacion": a["IdAsociacion"],
                        "mensaje": "Sin descripción; revisar con sentido clínico si la asociación es justificable.",
                        "asociacion": a,
                    }
                )
    return hallazgos


def detectar_posible_fusion_conceptos(entidades: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Regla R5 (heurística sobre el nombre): posibles conceptos independientes fusionados en una entidad.

    Excepción legítima no detectable automáticamente: combinaciones patológicas
    conjuntas de un mismo proceso (p. ej. "Patología Beta-amiloide y Tau").
    Requiere revisión manual, esto solo señala candidatos.
    """
    hallazgos = []
    for e in entidades:
        nombre = e.get("Entidad", "")
        if " y " in nombre or " / " in nombre:
            hallazgos.append(
                {
                    "regla": "R5",
                    "id_entidad": e.get("IdEntidad"),
                    "nombre": nombre,
                    "mensaje": "Contiene ' y '/' / '; revisar si son dos conceptos independientes.",
                }
            )
    return hallazgos


def detectar_tipo_singular_plural_sospechoso(entidades: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Regla R6 (heurística): nombres en plural/genéricos con un tipo que no es Group*.

    Ajustar `IDS_TIPO_GROUP` en docs/copenmed/PLAYBOOK.md sección 3 si se
    confirman más IDs de tipos Group*.
    """
    IDS_TIPO_GROUP = {13, 22}  # GroupOfTreatments, GroupOfDiseases (ver PLAYBOOK.md)
    prefijos_plural = ("fármacos", "farmacos", "análisis", "analisis", "pruebas de")
    hallazgos = []
    for e in entidades:
        nombre = e.get("Entidad", "")
        tipo = e.get("IdTipoEntidad")
        if any(nombre.lower().startswith(p) for p in prefijos_plural) and tipo not in IDS_TIPO_GROUP:
            hallazgos.append(
                {
                    "regla": "R6",
                    "id_entidad": e.get("IdEntidad"),
                    "nombre": nombre,
                    "id_tipo_entidad": tipo,
                    "mensaje": "Nombre parece plural/genérico; revisar si el tipo debería ser Group*.",
                }
            )
    return hallazgos


def detectar_relaciones_sin_direccion_clara(client, ids_entidad: list[int], id_estudiante: int | None = None) -> list[dict[str, Any]]:
    """Regla R13: 'is seen with' y similares están prohibidos por defecto, no solo desaconsejados."""
    id_estudiante = id_estudiante or client.id_estudiante
    TIPOS_PROHIBIDOS = {"Disease1 is seen with Disease2", "Group1 is seen with Group2"}
    hallazgos = []
    for id_entidad in ids_entidad:
        resp = client.buscar_asociaciones(id_entidad1=id_entidad, id_estudiante=id_estudiante, page_size=200)
        for a in resp["data"]:
            if a.get("TipoAsociacion") in TIPOS_PROHIBIDOS:
                hallazgos.append(
                    {
                        "regla": "R13",
                        "id_asociacion": a["IdAsociacion"],
                        "mensaje": "Tipo sin dirección/orden claro, prohibido por defecto; buscar alternativa causal/evolutiva/diagnóstica/jerárquica.",
                        "asociacion": a,
                    }
                )
    return hallazgos


def detectar_relaciones_debiles(client, ids_entidad: list[int], id_estudiante: int | None = None, umbral: float = 0.4) -> list[dict[str, Any]]:
    """Regla R14: no mantener asociaciones con Nivel por debajo del umbral (por defecto 0.4)."""
    id_estudiante = id_estudiante or client.id_estudiante
    hallazgos = []
    for id_entidad in ids_entidad:
        resp = client.buscar_asociaciones(id_entidad1=id_entidad, id_estudiante=id_estudiante, page_size=200)
        for a in resp["data"]:
            nivel = a.get("Nivel")
            if nivel is not None and nivel < umbral:
                hallazgos.append(
                    {
                        "regla": "R14",
                        "id_asociacion": a["IdAsociacion"],
                        "mensaje": f"Nivel {nivel} por debajo del umbral {umbral}; revisar si debe reforzarse o eliminarse.",
                        "asociacion": a,
                    }
                )
    return hallazgos


def buscar_candidatos_duplicado(client, terminos: list[str], page_size: int = 20) -> dict[str, list[dict[str, Any]]]:
    """Regla R11: antes de crear una entidad nueva, buscar candidatos por nombre/sinónimo.

    `terminos` es una lista de cadenas a probar (nombre completo, sinónimos,
    traducción). Devuelve, por término, las entidades que ya existen con un
    nombre parecido — para revisión manual antes de decidir si es un
    duplicado. No decide nada por sí solo.
    """
    return {termino: client.buscar_entidades(filtro=termino, page_size=page_size)["data"] for termino in terminos}


def auditoria_completa(client, entidades: list[dict[str, Any]]) -> dict[str, Any]:
    """Ejecuta todas las auditorías de solo lectura y devuelve un informe único.

    `entidades` debe ser la lista de objetos entidad propios (con al menos
    IdEntidad, Entidad, IdTipoEntidad), p. ej. el resultado de
    `client.buscar_entidades(id_estudiante=..., estado=0)["data"]`.
    """
    ids_entidad = [e["IdEntidad"] for e in entidades]
    return {
        "conteo_asociaciones": contar_asociaciones(client, ids_entidad),
        "R2_disease_con_hijos": detectar_disease_con_hijos(client, ids_entidad),
        "R3_R8_pares_multiples": detectar_pares_multiples(client, ids_entidad),
        "R4_causalidad_invertida": detectar_causalidad_invertida(client, ids_entidad),
        "R5_posible_fusion_conceptos": detectar_posible_fusion_conceptos(entidades),
        "R6_tipo_sospechoso": detectar_tipo_singular_plural_sospechoso(entidades),
        "R10_sin_descripcion": detectar_asociaciones_sin_descripcion(client, ids_entidad),
        "R13_sin_direccion_clara": detectar_relaciones_sin_direccion_clara(client, ids_entidad),
        "R14_relaciones_debiles": detectar_relaciones_debiles(client, ids_entidad),
    }
