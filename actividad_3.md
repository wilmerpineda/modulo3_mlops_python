# Actividad 3. Operar y actualizar un clasificador de forma controlada

## Propósito y modalidad
Proyecto colaborativo, **tres integrantes**, **dos semanas**, **12–16 horas por estudiante**. El porcentaje dentro del curso queda pendiente de syllabus; los pesos siguientes se aplican dentro de esta actividad.

Partir de `actividad_3/proyecto_inicial`. El objetivo es completar sus tareas de operación, no reconstruir desde cero un clasificador. El libro resuelve ejemplos formativos; el equipo debe aportar pruebas, experimentos y decisiones propias.

## Trabajo requerido

### Semana 1: observar
Crear repositorio accesible al docente y TEAM.md. Ejecutar baseline, revisar exclusiones y snapshot. Completar reportes estable/shift/degraded, evaluación de etiquetas tardías y auditoría por edad. Añadir una prueba de datos inválidos y otra de un caso de evaluación insuficiente. Iniciar Compose, generar tráfico y conservar evidencia del dashboard y de una alerta.

### Semana 2: automatizar y decidir
Completar el workflow CI y activar manualmente retraining. Entrenar el bosque candidato, comparar y justificar aceptación o rechazo. Implementar y probar el gate del proyecto inicial. Ensayar promoción de réplica y rollback con versión servida comprobada. Realizar carga con dos concurrencias, un informe de incidente y model card.

Rotar los roles de implementación, revisión y operación. Cada integrante debe aportar al menos un PR sustancial y una revisión razonada; un cambio cosmético no demuestra participación equivalente.

## Entrega

1. Enlace al repositorio y commit final, con acceso para el docente.
2. README reproducible, lock, snapshot y manifiesto, TEAM.md y enlaces a PR.
3. Código, pruebas completas y enlaces a ejecuciones reales de CI y retraining.
4. Reportes HTML/JSON de drift y tabla interpretada de desempeño y equidad.
5. Dashboard, evidencia de alerta y resultados de carga; indicar equipo, concurrencia y duración.
6. Comparación de modelos, decisión motivada y registro de promoción/rollback.
7. Model card e informe de incidente de 2–3 páginas; demostración de 5–7 minutos o video equivalente.

Las capturas acompañan los archivos reproducibles. No se exige proveedor cloud, gasto ni repositorio público si el acceso al docente está garantizado. Se acepta rechazar el candidato cuando la evidencia lo justifica.

## Rúbrica analítica

Cada criterio se evalúa en cuatro niveles: **Destacado (100 % del peso)**, **Logrado (80 %)**, **En desarrollo (50 %)** e **Insuficiente (0 %)**. La calificación es la suma de peso × factor de nivel; si se requiere escala 0–5, dividir el puntaje sobre 100 entre 20.

| Criterio | Peso | Destacado | Logrado | En desarrollo | Insuficiente |
|---|---:|---|---|---|---|
| Monitoreo e interpretación | 25 | Tres escenarios, alerta y dashboard reproducibles; diferencia causas y límites | Reportes y dashboard válidos, interpretación correcta | Evidencia parcial o confunde señal e impacto | Sin monitoreo ejecutable |
| CI/CD y pruebas | 25 | CI real, pruebas de fallos y retraining con artefactos trazables | CI y retraining ejecutados, pruebas esenciales completas | Workflow parcial o faltan casos de fallo | Sin CI verificable o pruebas no ejecutan |
| Actualización y recuperación | 20 | Gate probado, decisión sólida y rollback confirmado en API | Comparación y ensayo de promoción/rollback correctos | Cambia archivos sin verificar versión servida o gate incompleto | Promueve sin controles o no recupera |
| Gobernanza y equidad | 15 | Model card, grupos con denominadores y límites, mitigación contrastable | Documentación y análisis por grupos correctos | Métricas sin contexto o responsabilidades incompletas | Sin trazabilidad ni análisis de grupos |
| Reproducibilidad y equipo | 15 | Tercero reproduce, PR revisados, carga e incidente bien documentados | README funcional y participación comprobable | Requiere asistencia o evidencia de equipo parcial | No inicia o no hay evidencia de colaboración |

Una ausencia afecta el criterio correspondiente; no se inventan penalizaciones globales adicionales. El docente verificará que las evidencias correspondan al commit entregado.

## Límites de integridad
Identificar datos o etiquetas simulados. No reportar una ejecución de GitHub o contenedores que no ocurrió. No presentar cambios de formato como resultados nuevos. Explicar fuentes externas y contribuciones de herramientas utilizadas.
