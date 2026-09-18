# COpenMed — estado actual de la sesión

**Última actualización**: 2026-09-18 (migración del documento de traspaso
original a esta estructura; ningún dato de COpenMed se ha tocado en esta
migración).

## Identidad

- Usuario: Alexander Pabón Farias
- `IdEstudiante`: 143 — **confirmado por el usuario el 2026-09-18, usar siempre**
  este valor por defecto en todas las llamadas de creación/filtrado
  (ya es el default en `scripts/copenmed/client.py`).

## Dependencia pendiente: export de entidades indexadas

La política de duplicados (regla R11 del playbook) requiere poder buscar
rápido entre TODAS las entidades indexadas en COpenMed, no solo las propias.
En la sesión anterior se usó un CSV export (~14.740 entidades: `id,nombre,
categoria`). **Aún no se ha recibido ese archivo en esta sesión.** Sin él,
la comprobación de duplicados/candidatos tendrá que hacerse vía
`entidad/?filter=` contra la API (más lento, pero funcional con las
cookies). Pedir al usuario el CSV en cuanto se retome trabajo real si quiere
acelerar el flujo.

## IDs clave de referencia

| Código | ID COpenMed | Notas |
|---|---|---|
| BlockL1-9C4 (Trastornos de las vías o centros visuales) | 18065 | Bloque, ~155+ asociaciones |
| BlockL1-9C6 (Glaucoma o sospecha de glaucoma) | 18075 | Bloque, ~155+ asociaciones |
| Enfermedades del sistema visual (Cap. 09, padre de 9C4) | 17818 | — |
| Ataxias espinocerebelosas (SCA) | 17941 | Corregida a GroupOfDiseases (ver CHANGELOG) |
| Dystonia-plus (de otro estudiante, id 105) | 16388 | Sigue mal tipada como Disease; no corregible (no es propia) |
| Paroxysmal dystonia (de otro estudiante) | 16390 | — |

*(IDs de las 28 entidades del bloque 9C4 y las 54 del bloque 9C6: consultar
`entidad/?filter=CIE-11:` — no listadas aquí por espacio. Si se vuelve a
trabajar sobre ellas, considerar volcarlas a una tabla en este archivo o a
`scripts/copenmed/data/` para no depender de la memoria de la conversación —
ver regla R7 del playbook.)*

## Checklist pendiente

- [ ] Descripciones bilingües de: 17989, 17990, 17991, 17994, 17999 (aún sin descripción larga)
- [ ] 18031 "Síndrome Clínicamente Aislado (CIS)": sin ninguna asociación propia.
      Propuesta ya identificada: añadir asociación con Esclerosis Múltiple
      (16527, CIE-11 8A40) como precursor clásico. No ejecutada.
- [ ] Revisión de calidad de **contenido clínico** (no solo estructura) del
      resto de las ~93 entidades no aprobadas. Solo se completó un barrido
      estructural (duplicados/ciclos/direcciones vía reglas R2-R10 del
      playbook), no una revisión clínica exhaustiva de cada descripción.
- [ ] Confirmar con el usuario si sigue habiendo entidades pendientes del
      grupo de trastornos del movimiento/neurodegenerativos no cubiertas por
      el checklist de `CHANGELOG.md`.

## Preferencias de trabajo confirmadas por el usuario

- **Autonomía**: auditar y listar primero; corregir solo tras confirmación
  explícita del usuario (por hallazgo o por lote).
- **Eliminación de entidades**: si al corregir una relación una entidad se
  queda sin ninguna asociación, avisar antes de eliminarla (dar opción a
  añadir asociaciones en vez de borrar).
- **Persistencia de contexto**: en el repo (esta carpeta), no como documento
  pegado en el chat.
- **Duplicados al crear entidades (2026-09-18, regla R11 del playbook)**:
  siempre buscar sinónimos/candidatos similares antes de crear una entidad
  nueva. Si es duplicado de una entidad ajena o ya aprobada, no crearla ni
  borrarla — volcar todo su contenido en la entidad correcta, dejar la
  duplicada solo con el nombre, y avisar al usuario para que su tutor la
  elimine.
- **Prioridad de entidades antiguas (regla R12)**: ante solapamiento,
  reutilizar/enlazar la entidad preexistente en vez de crear una nueva,
  salvo que su tipo (`IdTipoEntidad`) sea incorrecto para el uso necesario.
- **Relaciones sin dirección clara (regla R13)**: "is seen with" (291/294) y
  similares, prohibidas por defecto — agotar alternativas antes de usarlas,
  y si no hay ninguna razonable, no crear la asociación.
- **Fuerza de las asociaciones (regla R14)**: `Nivel` entre 0 y 1 (1 =
  fuerte); nunca por debajo de `0.4`; siempre con punto decimal, no coma.
- **No forzar contenido (regla R15)**: objetivo orientativo de ≥10
  asociaciones entrantes y ≥10 salientes por entidad, pero nunca inventar
  relaciones/fuentes/datos para alcanzarlo.
- **Contenido mínimo por entidad (regla R16)**: nombres ES/EN con sinónimos
  indexados por especificidad (0/1/2, campo API pendiente de confirmar),
  código CIE junto al nombre, descripciones científicas ES/EN, y 5 fuentes
  fiables (clínicas, laboratorios, papers o divulgación científica seria).

## Registro de esta sesión

El historial en `CHANGELOG.md` bajo "Sesión en claude.ai... anterior a
2026-09-18" es de una sesión distinta (Claude in Chrome) y no cuenta como
trabajo de esta sesión de Claude Code. A partir de ahora, cada operación de
escritura real sobre COpenMed en esta sesión se añade en vivo (no al final)
a una sección nueva de `CHANGELOG.md` fechada `2026-09-18 — trabajo de
entidades (sesión en curso)`. Esa sección es la fuente para el registro
completo que el usuario pedirá al cierre de la conversación.

## Próximo paso decidido

El 2026-09-18 se decidió cerrar primero el flujo de trabajo (esta
migración) antes de retomar trabajo real sobre entidades. Al empezar la
siguiente sesión de trabajo real, preguntar alcance: ¿terminar pendientes
9C4/9C6 (este checklist) o abrir un bloque CIE-11 nuevo?
