"""Cliente HTTP fino para la API de COpenMed.

Requiere cookies de sesión exportadas por el usuario (ver
docs/copenmed/README.md) — no hay login por API ni token Bearer conocido.

Cada operación de escritura (POST/PUT/DELETE) se registra en un log JSONL
local para poder comprobar, tras un fallo de red, si la operación anterior
ya se guardó antes de reintentar (ver "patrones de trabajo eficientes",
punto 6, en docs/copenmed/PLAYBOOK.md) y así evitar duplicados (regla R8).
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import requests

BASE_URL = "https://copenmed.org/CeuopenmedAPI/backend/web/"
DEFAULT_LOG_PATH = Path("docs/copenmed/.operations.jsonl")
DEFAULT_ID_ESTUDIANTE = 143


class CopenMedClient:
    def __init__(
        self,
        cookies_path: str | Path,
        log_path: str | Path = DEFAULT_LOG_PATH,
        id_estudiante: int = DEFAULT_ID_ESTUDIANTE,
    ) -> None:
        self.session = requests.Session()
        self._load_cookies(Path(cookies_path))
        self.log_path = Path(log_path)
        self.id_estudiante = id_estudiante

    def _load_cookies(self, path: Path) -> None:
        data = json.loads(path.read_text())
        if isinstance(data, list):
            for c in data:
                self.session.cookies.set(c["name"], c["value"], domain=c.get("domain"))
        else:
            for name, value in data.items():
                self.session.cookies.set(name, value)

    def _log_operation(self, method: str, url: str, body: Any, response: Any) -> None:
        entry = {"ts": time.time(), "method": method, "url": url, "body": body, "response": response}
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def _request(self, method: str, path: str, params: dict | None = None, json_body: dict | None = None) -> Any:
        url = BASE_URL + path
        resp = self.session.request(method, url, params=params, json=json_body)
        resp.raise_for_status()
        data = resp.json()
        if method in ("POST", "PUT", "DELETE"):
            self._log_operation(method, resp.url, json_body, data)
        return data

    # --- entidad ---
    def buscar_entidades(
        self, *, filtro=None, id_entidad=None, id_estudiante=None, estado=None, page=0, page_size=50
    ) -> Any:
        params: dict[str, Any] = {"pagination[page]": page, "pagination[pageSize]": page_size}
        if filtro is not None:
            params["filter"] = filtro
        if id_entidad is not None:
            params["search[IdEntidad]"] = id_entidad
        if id_estudiante is not None:
            params["search[IdEstudiante]"] = id_estudiante
        if estado is not None:
            params["search[Estado]"] = estado
        return self._request("GET", "entidad/", params=params)

    def crear_entidad(self, entidad: str, id_tipo_entidad: int, estado: int = 0, id_estudiante: int | None = None) -> Any:
        body = {
            "Entidad": entidad,
            "IdTipoEntidad": id_tipo_entidad,
            "IdEstudiante": id_estudiante or self.id_estudiante,
            "Estado": estado,
        }
        return self._request("POST", "entidad/create", json_body=body)

    def actualizar_entidad(self, id_entidad: int, **campos: Any) -> Any:
        return self._request("PUT", "entidad/update", params={"id": id_entidad}, json_body=campos)

    def eliminar_entidad(self, id_entidad: int) -> Any:
        return self._request("DELETE", "entidad/delete", params={"id": id_entidad})

    # --- detalle-entidad (nombres/sinónimos por idioma) ---
    def listar_detalle_entidad(self, id_entidad: int) -> Any:
        return self._request("GET", "detalle-entidad/", params={"search[IdEntidad]": id_entidad})

    def actualizar_detalle_entidad(self, id_recurso: int, entidad_texto: str) -> Any:
        return self._request("PUT", "detalle-entidad/update", params={"id": id_recurso}, json_body={"Entidad": entidad_texto})

    def eliminar_detalle_entidad(self, id_recurso: int) -> Any:
        return self._request("DELETE", "detalle-entidad/delete", params={"id": id_recurso})

    def descripciones_entidad(self, id_entidad: int) -> Any:
        return self._request("GET", f"entidad/descripciones/{id_entidad}")

    # --- asociacion ---
    def buscar_asociaciones(
        self, *, id_entidad1=None, id_entidad2=None, id_estudiante=None, page=0, page_size=100
    ) -> Any:
        params: dict[str, Any] = {"pagination[page]": page, "pagination[pageSize]": page_size}
        if id_entidad1 is not None:
            params["search[IdEntidad1]"] = id_entidad1
        if id_entidad2 is not None:
            params["search[IdEntidad2]"] = id_entidad2
        if id_estudiante is not None:
            params["search[IdEstudiante]"] = id_estudiante
        return self._request("GET", "asociacion/", params=params)

    def contar_asociaciones_propias(self, id_entidad: int, id_estudiante: int | None = None) -> int:
        """Conteo fiable (regla R1): NO usar evaluated-associate-entitys-*, que subcuenta."""
        id_estudiante = id_estudiante or self.id_estudiante
        salientes = self.buscar_asociaciones(id_entidad1=id_entidad, id_estudiante=id_estudiante, page_size=1)
        entrantes = self.buscar_asociaciones(id_entidad2=id_entidad, id_estudiante=id_estudiante, page_size=1)
        return salientes["totalCount"] + entrantes["totalCount"]

    def tipos_asociacion_validos(self, id_entidad1: int, id_entidad2: int) -> Any:
        return self._request("GET", f"tipo-asociacion/relationship/{id_entidad1}/{id_entidad2}")

    def crear_asociacion(
        self,
        id_entidad1: int,
        id_entidad2: int,
        id_tipo_asociacion: int,
        descripcion: str | None = None,
        nivel: int = 1,
        estado: int = 1,
        id_estudiante: int | None = None,
    ) -> Any:
        body = {
            "IdEntidad1": id_entidad1,
            "IdEntidad2": id_entidad2,
            "IdTipoAsociacion": id_tipo_asociacion,
            "Nivel": nivel,
            "Descripcion": descripcion,
            "IdEstudiante": id_estudiante or self.id_estudiante,
            "Estado": estado,
        }
        return self._request("POST", "asociacion/create", json_body=body)

    def eliminar_asociacion(self, id_asociacion: int) -> Any:
        return self._request("DELETE", "asociacion/delete", params={"id": id_asociacion})

    def reemplazar_asociacion(self, id_asociacion_vieja: int, **kwargs_nueva: Any) -> Any:
        """No existe update fiable para asociaciones: patrón siempre usado es delete + create."""
        self.eliminar_asociacion(id_asociacion_vieja)
        return self.crear_asociacion(**kwargs_nueva)

    # --- recurso (fuentes bibliográficas) ---
    def crear_recurso(
        self, id_entidad: int, url: str, nivel: int = 1, is_image: int = 0, id_estudiante: int | None = None, estado: int = 1
    ) -> Any:
        body = {
            "IdEntidad": id_entidad,
            "Nivel": nivel,
            "URL": url,
            "IsImage": is_image,
            "IdEstudiante": id_estudiante or self.id_estudiante,
            "Estado": estado,
        }
        return self._request("POST", "recurso/create", json_body=body)

    def listar_recursos(self, id_entidad: int, limit: int = 20) -> Any:
        return self._request("GET", "recurso/", params={"search[IdEntidad]": id_entidad, "search[limit]": limit})
