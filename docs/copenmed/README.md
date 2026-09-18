# COpenMed — panel de traspaso entre sesiones

Este directorio sustituye al antiguo "documento de traspaso" pegado como texto al
inicio de cada sesión. Al vivir dentro del repo, el traspaso entre sesiones de
Claude Code es simplemente `git pull` + leer `STATE.md`, en vez de re-pegar un
`.md` de 10 secciones cada vez.

## Qué leer, y en qué orden

1. **`STATE.md`** — léelo siempre primero. Qué bloque/entidades están activos,
   checklist pendiente, IDs clave de la sesión en curso. Es lo único que
   cambia cada sesión de trabajo.
2. **`PLAYBOOK.md`** — referencia estable: arquitectura, endpoints de la API,
   catálogos de tipos, reglas de corrección (errores ya cometidos y cómo
   evitarlos) y patrones de trabajo eficientes. Solo se actualiza cuando se
   descubre un endpoint nuevo, un tipo nuevo o un patrón de error nuevo.
3. **`CHANGELOG.md`** — historial append-only de correcciones ya aplicadas.
   No se relee salvo para comprobar si algo concreto ya se corrigió; nunca se
   reescribe con retroactividad.

## Autenticación

COpenMed se autentica por cookies de sesión de navegador, no hay login por API
ni token Bearer conocido. Para que el cliente (`scripts/copenmed/client.py`)
pueda operar:

1. El usuario exporta las cookies de su sesión ya logueada en
   `https://copenmed.org` (p. ej. con una extensión tipo "Cookie-Editor",
   formato Netscape o JSON).
2. Guarda el export como `docs/copenmed/.cookies.json` (o la ruta que se le
   indique en el momento) — **este archivo NUNCA se commitea**, ver
   `.gitignore`. Trátalo como una credencial: no lo imprimas en logs, no lo
   pegues en un commit, no lo mandes a servicios externos.
3. Las cookies de sesión caducan; si el cliente empieza a recibir 401/403 o
   redirecciones a login, pide al usuario que las re-exporte.

No se intenta login automatizado vía navegador (Playwright) porque esta sesión
corre en un contenedor remoto y efímero sin perfil de navegador del usuario ni
forma de completar un login interactivo — las cookies exportadas son el único
mecanismo practicable aquí.

## Nivel de autonomía por defecto

Salvo instrucción contraria explícita del usuario en la sesión: **auditar y
listar primero**. Cualquier script de auditoría (`scripts/copenmed/audit.py`)
debe producir un informe de hallazgos de solo lectura; las correcciones
(`create`/`update`/`delete` contra la API) solo se ejecutan tras confirmación
explícita del usuario por hallazgo o por lote — nunca de forma silenciosa.
