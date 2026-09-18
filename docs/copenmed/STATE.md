# COpenMed — estado actual de la sesión

**Última actualización**: 2026-09-18 (migración del documento de traspaso
original a esta estructura; ningún dato de COpenMed se ha tocado en esta
migración).

## Identidad

- Usuario: Alexander Pabón Farias
- `IdEstudiante`: 143 *(pendiente de reconfirmar por el usuario al retomar trabajo real, ver `README.md`)*

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

## Próximo paso decidido

El 2026-09-18 se decidió cerrar primero el flujo de trabajo (esta
migración) antes de retomar trabajo real sobre entidades. Al empezar la
siguiente sesión de trabajo real, preguntar alcance: ¿terminar pendientes
9C4/9C6 (este checklist) o abrir un bloque CIE-11 nuevo?
