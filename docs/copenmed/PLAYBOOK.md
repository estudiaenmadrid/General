# COpenMed — playbook técnico (referencia estable)

Plataforma: `https://copenmed.org`. SPA Angular con rutas hash. Grafo de
conocimiento médico colaborativo: entidades (enfermedades, síntomas, pruebas,
tratamientos, causas, anatomía, etc.) conectadas por asociaciones tipadas y
direccionales.

Este archivo solo cambia cuando se descubre un endpoint, tipo o patrón de
error **nuevo**. El estado de la sesión en curso vive en `STATE.md`, no aquí.

---

## 1. Arquitectura

- **Frontend**: SPA Angular, rutas hash (`https://copenmed.org/#/...`).
- **Backend API**: `https://copenmed.org/CeuopenmedAPI/backend/web/`
- **Auth**: cookies de sesión de navegador (`credentials:'include'`). No hay
  login por API ni token Bearer conocido. Ver `README.md` de este directorio
  para cómo se resuelve en Claude Code.

Rutas del frontend (útiles solo para verificación visual manual):
- Ver entidad: `.../#/VisorEntidad/{id}/22`
- Editar descripciones por idioma: `.../#/additionalInfo/{id}/22/2`

---

## 2. Endpoints de API

Base: `https://copenmed.org/CeuopenmedAPI/backend/web/`

### Entidades (`entidad`)
- Buscar por texto: `GET entidad/?pagination[page]=0&pagination[pageSize]=N&filter={texto}`
- Buscar por ID exacto: `GET entidad/?pagination[page]=0&pagination[pageSize]=N&search[IdEntidad]={id}`
- Filtrar por estudiante y estado: `GET entidad/?search[IdEstudiante]={id}&search[Estado]=0&pagination[page]=0&pagination[pageSize]=100`
  (Estado=0 → no aprobada/pendiente; Estado=1 → aprobada/activa, según contexto)
- Crear: `POST entidad/create` body `{Entidad, IdTipoEntidad, IdEstudiante, Estado}` → devuelve `IdEntidad`
- Actualizar: `PUT entidad/update?id={id}` body `{IdTipoEntidad, ...}` — **`id` va en query string, no en el body**
- Eliminar: `DELETE entidad/delete?id={id}` — sin body

### Nombres/sinónimos por idioma (`detalle-entidad`)
El nombre visible en el buscador sale de aquí, no del campo largo de `entidad`.
- Ver registros de una entidad: `GET detalle-entidad/?search[IdEntidad]={id}` → `IdRecurso`, `IdIdioma` (3=Español, 4=English), `Entidad`, `IdTipoEntidad`
- Actualizar un nombre/sinónimo: `PUT detalle-entidad/update?id={IdRecurso}` body `{Entidad: 'texto'}`
- Eliminar un sinónimo: `DELETE detalle-entidad/delete?id={IdRecurso}`
- Descripciones largas: `GET entidad/descripciones/{id}` → `[]` si no tiene descripción larga en ningún idioma.
  **Pendiente de investigar**: no se localizó endpoint API puro para *escribir*
  la descripción larga (solo vía UI en `additionalInfo/{id}/22/2`). Si se va a
  trabajar sin navegador, confirmar esto antes de asumir que no existe.

### Asociaciones (`asociacion`)
- Por par de entidades: `GET asociacion/?search[IdEntidad1]={id1}&search[IdEntidad2]={id2}` → `IdAsociacion`, `Descripcion`, `TipoAsociacion`, `IdEstudiante`, ...
- Salientes de una entidad: `GET asociacion/?search[IdEntidad1]={id}` — **usar `.totalCount`, no `.data.length`**
- Entrantes: `GET asociacion/?search[IdEntidad2]={id}`
- Filtrar por estudiante propio: añadir `&search[IdEstudiante]={id}`
- Crear: `POST asociacion/create` body `{IdEntidad1, IdEntidad2, IdTipoAsociacion, Nivel, Descripcion, IdEstudiante, Estado:1}`
- Eliminar: `DELETE asociacion/delete?id={IdAsociacion}`
- **No hay update fiable para asociaciones.** Patrón siempre usado: **delete + create** (borrar la incorrecta, crear la correcta).

### Tipos de asociación válidos por par (`tipo-asociacion`)
`GET tipo-asociacion/relationship/{IdEntidad1}/{IdEntidad2}` → lista de
`IdTipoAsociacion` + texto válidos para ESE PAR en ESA DIRECCIÓN, según los
tipos de entidad de ambas. **Fuente de verdad**: consultar SIEMPRE antes de
crear una asociación. Si el tipo necesario solo existe en la dirección
contraria, invertir `IdEntidad1`/`IdEntidad2` en la creación.

Algunos tipos vienen marcados `(NO USAR, cambiar X a Group)` — es un aviso de
que el tipo de la entidad de destino está mal configurado para ese uso.
Evitarlos; buscar una alternativa semánticamente cercana en la misma lista.

### Recursos/fuentes bibliográficas (`recurso`)
- Crear: `POST recurso/create` body `{IdEntidad, Nivel, URL, IsImage:0, IdEstudiante, Estado:1}`
- Listar: `GET recurso/?search[IdEntidad]=N&search[limit]=20`

### Notas generales de la API
- Listas devuelven `{status, data:[...], page, size, totalCount, totalData}` — usar `totalCount` cuando la paginación pueda truncar.
- Verbos HTTP estrictos por endpoint; verbo equivocado → `405/400`.
- `id` de `update`/`delete` va casi siempre en **query string**, no en el body.

---

## 3. Catálogo de tipos de entidad (`IdTipoEntidad`)

| ID | Nombre |
|---|---|
| 6 | Disease |
| 22 | GroupOfDiseases |
| 12 | Treatment |
| 13 | GroupOfTreatments |
| 20 | Activity |

Resto (Symptom, Test, Cause, Anatomy, Population, Substance, Condition,
TestResult, Specialty, GroupOfTests, Gene, Molecule, Pathogen, Physiological
feature, GroupOfSubstances...): IDs no memorizados en su totalidad. Para
averiguar el ID de un tipo, buscar una entidad existente de ese tipo con
`entidad/?filter=...` y leer `IdTipoEntidad`. Añadir aquí cualquier ID nuevo
que se confirme.

---

## 4. Catálogo de tipos de asociación (`IdTipoAsociacion`) más usados

| ID | Texto | Uso típico |
|---|---|---|
| 8 | Disease1 is similar to Disease2 | Sinónimo clínico / diferencial cercano |
| 9 | Disease1 may evolve to Disease2 | Progresión |
| 22 | Disease1 may evolve and coexist with Disease2 | Progresión con coexistencia; sustituto seguro de "subtype of" cuando el destino no es Group |
| 30 | Disease is diagnosed with this Test | — |
| 31 | Disease can be treated with Treatment | — |
| 46 | Risk is associated to Disease | — |
| 56 | Pathogen causes disease | — |
| 62 | Cause may cause Disease | **Dirección correcta para causa → enfermedad (ver regla 4 en errores)** |
| 76 | Group1 is a subgroup of Group2 | Jerarquía Group-Group |
| 77 | Disease belongs to Group | Jerarquía hijo(Entidad1)→padre(Entidad2) |
| 79 | Cause can cause this Group | — |
| 84 | Group may cause symptom | — |
| 125 | Group belongs to the domain of Specialty | — |
| 129 | Group can be treated with Treatment | — |
| 148 | Group can be diagnosed with Test | — |
| 179 | Disease causes Symptom | — |
| 236 | Disease1 may cause Disease2 to get worse | — |
| 241 | Group of treatments may cause Group of diseases | — |
| 260 | Group can only be observed in Population | — |
| 291 | Disease1 is seen with Disease2 | Evitar como opción por defecto; buscar tipo más preciso siempre que exista |
| 294 | Group1 is seen with Group2 | Igual, evitar como comodín |
| 47 | Disease1 is a subtype of Disease2 **(NO USAR, cambiar Disease2 a Group)** | Señal de que el destino debería ser GroupOfDiseases; usar 22 o 9 como alternativa razonable si no se puede corregir el tipo (p. ej. entidad de otro estudiante) |

---

## 5. Reglas de corrección (errores ya cometidos — no repetirlos)

Cada regla es una función de auditoría candidata en `scripts/copenmed/audit.py`.

### R1 — Conteo fiable de asociaciones
`asociacion/evaluated-associate-entitys-a/{id}` y `...-b/{id}` **no son
fiables** (dieron cifras muy por debajo de la realidad). Método correcto:
```
GET asociacion/?search[IdEntidad1]={id}&search[IdEstudiante]={idEstudiante} → .totalCount
GET asociacion/?search[IdEntidad2]={id}&search[IdEstudiante]={idEstudiante} → .totalCount
total real = suma de ambos
```

### R2 — Jerarquía Disease/Group mal tipada
Si una entidad `Disease` tiene una asociación `Disease belongs to Group`
apuntando hacia ella (otra entidad es su hija), debería ser `GroupOfDiseases`.
Chequeo: para cada Disease propia, `asociacion/?search[IdEntidad2]={id}`,
filtrar `TipoAsociacion === 'Disease belongs to Group'`; si hay alguna,
proponer cambio de tipo a GroupOfDiseases.

### R3 — Ciclos lógicos / contradicciones jerárquicas
Patrón: `A belongs to Group B` **y a la vez** `B may evolve and coexist with A`
(un grupo no "evoluciona hacia" su propio miembro). Chequeo: agrupar todas las
asociaciones propias (salientes+entrantes) por "entidad contraria"; si una
pareja tiene más de una asociación, revisar manualmente (puede ser ciclo,
duplicado, o dos relaciones legítimamente distintas).

### R4 — Direcciones de causalidad invertidas (patrón sistemático, el más repetido)
"Mutación X → Enfermedad" creada como `Disease may cause Cause` (mutación
como Entidad2) es casi siempre un error. Correcto: causa como `IdEntidad1`,
tipo `62 Cause may cause Disease`, enfermedad como `IdEntidad2`. Mismo
criterio para hallazgos patológicos ("Patología X" como mecanismo/causa de la
enfermedad). Chequeo: buscar asociaciones propias con
`TipoAsociacion === 'Disease may cause Cause'` o `'Group may cause Cause'` —
casi siempre están invertidas.

### R5 — Entidades que mezclan varios conceptos independientes
Señal: el nombre contiene " y " o " / " uniendo dos sustantivos
diagnosticables/tratables por separado (p. ej. "Consumo de alcohol y
cafeína" → dos `Activity` separadas). Excepción legítima: cuando " y "
describe una combinación patológica conjunta de un mismo proceso (p. ej.
"Patología Beta-amiloide y Tau" como firma histológica única de una
enfermedad) — ahí no separar. Mismo cuidado con `detalle-entidad`: varios
"sinónimos" en el mismo idioma pueden ser en realidad entidades clínicas
distintas mal fusionadas.

### R6 — Tipo de entidad completamente erróneo
Nombres en plural o genéricos ("Fármacos X", "Análisis de X") casi siempre
deberían ser tipo Group* (GroupOfTreatments, GroupOfTests), no el singular.
Revisar tipo de entidad vs. semántica del nombre.

### R7 — Confusión de IDs entre bloques trabajados en paralelo
Cuando se trabaja con varios bloques CIE-11 a la vez, llevar SIEMPRE una
tabla explícita código↔ID actualizada en `STATE.md` y releerla antes de cada
lote de operaciones — no confiar en la memoria de la conversación.

### R8 — Asociaciones exactamente duplicadas
Agrupar asociaciones propias por par de entidades; mismo par + mismo tipo
más de una vez → duplicado seguro, eliminar la más reciente. Mismo par +
tipos distintos → revisar manualmente (puede ser R3).

### R9 — Tipo de asociación que no encaja con la descripción
Releer siempre la `Descripcion` ya escrita antes de decidir/mantener un
`IdTipoAsociacion` — el tipo debe reflejar fielmente el texto, no solo "algo
que compile" (ej.: una asociación que habla de diagnóstico diferencial no
debería llevar un tipo de progresión/evolución).

### R10 — Asociaciones clínicamente cuestionables sin justificación
Cuando `Descripcion` es `null` y el tipo/contenido resulta clínicamente
dudoso al leerlo con sentido común médico, es señal de alarma: revisar y, si
no se puede justificar, proponer eliminación (nunca eliminar en autonomía si
el usuario pidió "auditar y listar primero", ver `README.md`).

---

## 6. Patrones de trabajo eficientes

1. **Caché local para búsqueda de candidatos**: si se dispone de un export
   (CSV/SQLite) de entidades, buscar ahí primero es mucho más rápido que
   `entidad/?filter=` repetido contra la API.
2. **Verificar antes de crear**: siempre `GET tipo-asociacion/relationship/{id1}/{id2}`
   antes de `POST asociacion/create`. Nunca crear "a ciegas".
3. **Lotes moderados**: agrupar 6-10 pares por llamada de verificación de
   tipos antes de crear el lote correspondiente, en vez de ir de uno en uno.
4. **No crear vínculos "hermana↔hermana"** entre subcategorías de un mismo
   bloque salvo que sea estrictamente jerárquico (padre-hijo) — instrucción
   explícita del usuario; genera ruido y puede producir ciclos (R3).
5. **Evitar "is seen with" (291/294) como comodín**: casi siempre existe un
   tipo más preciso (causal, evolutivo, diagnóstico) en
   `tipo-asociacion/relationship`. Revisar la lista completa antes de
   conformarse con "seen with".
6. **Reintentos tras fallo de red**: comprobar primero si la operación
   anterior sí se guardó (GET de verificación) antes de reintentar el mismo
   `create`, para no producir duplicados (R8). El cliente
   (`scripts/copenmed/client.py`) debe llevar un log de operaciones para
   esto — ver ese archivo.
