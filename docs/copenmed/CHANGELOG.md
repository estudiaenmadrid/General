# COpenMed — historial de correcciones aplicadas

Log append-only. No se reescribe retroactivamente; una corrección que resulta
incompleta o errónea se documenta como una entrada nueva, no editando la
entrada vieja.

## Sesión en claude.ai (Claude in Chrome) — anterior a 2026-09-18, fecha exacta no registrada

Corrección de errores de calidad en entidades no aprobadas del usuario
(IdEstudiante 143), tras feedback del tutor, sobre los bloques CIE-11 9C4 y
9C6 y un grupo previo de trastornos del movimiento/neurodegenerativos.

- [x] 17941 Ataxias espinocerebelosas: Disease → GroupOfDiseases + asociación con 2249 corregida (regla R2)
- [x] 17946, 17947 (PNKD/PED): ciclos lógicos eliminados (regla R3)
- [x] 17943 "Consumo de alcohol y cafeína": eliminada, dividida en 18416 (alcohol) + 18417 (cafeína), tipo Activity (regla R5)
- [x] 18356 (marcada BORRAR por el propio usuario en su día): eliminada
- [x] 18032 Fingolimod: Test → Treatment (regla R6)
- [x] 17999 Fármacos estimulantes: Treatment → GroupOfTreatments + asociación recreada (regla R6)
- [x] 17948: renombrada de "Psicoterapia / Terapia Cognitivo-Conductual (TCC)" a solo "Terapia Cognitivo-Conductual (TCC)" (ES y EN) + 6 asociaciones "prevents" → "can be treated with"
- [x] 18043, 18049, 18147-8041: duplicados exactos eliminados (regla R8)
- [x] 18016 ↔ 18340: ciclo lógico eliminado (regla R3)
- [x] 17940: dividida en 3 entidades (17940 solo, 18419 Mioclonía-distonía nueva, 18420 RDP nueva) + direcciones hacia 16388 corregidas (tipo 22) (regla R5)
- [x] 17967 (SCA3) ↔ 17941: dirección invertida corregida
- [x] 18021 ↔ 16503: tipo ajustado (evitando "NO USAR")
- [x] 18007 ↔ 16487, 18001 ↔ 16476, 18020 ↔ 16503, 18011 ↔ 1219: 4 mutaciones genéticas con dirección invertida corregidas (Cause→Disease, regla R4)
- [x] 18017 ↔ 16499, 18015 ↔ 16495: patologías (Beta-amiloide/Tau, Tau/TDP-43) con dirección invertida corregidas (regla R4)
- [x] 16417 ↔ 17976: tipo incorrecto corregido (17976 es un Test, no una Cause)
- [x] 17949 ↔ 16576 (PNES→Epilepsia): tipo ajustado a "is similar to" (regla R9)
- [x] 18064: bloque duplicado eliminado, 2 asociaciones huérfanas reasignadas a 18065 (regla R7)
- [x] 18147 (Catarata): 5 correcciones (midriático, condroitín, campo visual, ambliopía, jerarquía RAM) (regla R10)
- [x] Descripciones bilingües añadidas a: 17945, 17951, 17975, 17976 (de las 11 que no tenían)

Pendientes de esta sesión: ver checklist en `STATE.md`.

## 2026-09-18 — migración de flujo (sin tocar datos de COpenMed)

- Se recibió el documento de traspaso original (pegado en chat) y se dividió
  en `README.md` (onboarding/autenticación), `PLAYBOOK.md` (referencia
  estable) y este `CHANGELOG.md`, dentro de `docs/copenmed/` en el repo, para
  que el traspaso entre sesiones de Claude Code sea vía git en vez de
  re-pegar texto.
- No se realizó ninguna llamada a la API de COpenMed en este paso.
