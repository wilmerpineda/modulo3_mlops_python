# Tareas obligatorias

La API, el baseline, la instrumentación y los reportes básicos se entregan operativos. La entrega no está completa hasta resolver:

1. A3-01: implementar lifecycle.compare según las tolerancias, sin modificar scores ni usar test para decidir.
2. A3-02: prueba de promoción de réplica, rechazo de deterioro y rollback; verificar versión HTTP después de reinicio. Retirar skip. Añadir categoría nueva y ventana sin positivos.
3. A3-03: ejecutar pytest en CI, conservar enlaces al fallo y reparación; ejecutar retraining manual.
4. A3-04: interpretar reportes estable/shift/degraded; proponer persistencia y volumen mínimo con dos ventanas; no promover automáticamente por drift.
5. A3-05: generar tráfico, demostrar alerta y comparar carga con 1 y 4 clientes; conservar JSON separados.
6. A3-06: comparar bosque candidato, justificar decisión y ensayar promoción y rollback de réplica.
7. A3-07: completar model card, grupos con denominadores, informe de incidente, TEAM.md y revisión de PR.

El estado inicial tiene una prueba omitida deliberadamente. La entrega final debe tener cero omisiones deliberadas y ningún TODO obligatorio sin resolver. Un CI inicial que solo compila no demuestra que la actividad esté completa.
