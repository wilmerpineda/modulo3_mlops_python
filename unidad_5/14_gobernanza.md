# Auditoría, documentación y control de calidad

## Gobierno del modelo

Gobernanza es definir quién decide, con qué evidencia y bajo qué límites. Un directorio con versiones es útil, pero no constituye por sí mismo gobierno. La model card debe explicar propósito, población, exclusiones, métricas, riesgos, responsables y condiciones de retiro.

El registro de acciones guarda actor, motivo, fecha UTC y versión. El historial Git registra cambios de código; los manifiestos describen datos; los reportes documentan resultados. La cadena solo es útil si los identificadores se conectan. Una captura aislada no permite repetir la evaluación.

## Control de calidad antes de liberar
Confirmar esquema de datos, integridad del artefacto, compatibilidad de features y entorno. Revisar comportamiento de error y readiness. Verificar que el README contiene comandos desde un checkout limpio. Confirmar que los umbrales se fijaron sin usar la prueba final para elegirlos.

```{mermaid}
flowchart TD
 A[Datos y manifiesto] --> D[Expediente de versión]
 B[Commit y dependencias] --> D
 C[Métricas y análisis de grupos] --> D
 D --> E[Revisor]
 E --> F[Decisión documentada]
 F --> G[Operación y seguimiento]
```

## Retención y minimización
La API conserva identificador, probabilidad, decisión y versión, no el payload personal. Para evaluar drift real haría falta una captura de features con reglas de acceso y retención; el laboratorio usa lotes separados y no afirma monitoreo continuo de todas las entradas de la API. Esa separación se declara para no confundir demostración con plataforma completa.

La auditoría por edad utiliza el dataset offline. Para datos nuevos se necesitaría una unión autorizada con atributos de auditoría. No añadirlos a logs o etiquetas Prometheus por comodidad.

## Incidente y aprendizaje
Un informe breve incluye detección, impacto, línea de tiempo, causa probable, mitigación, evidencia de recuperación y acción preventiva con responsable. Evitar culpar a una persona como sustituto de analizar el sistema. Separar hechos observados de hipótesis.

**Ejercicio:** complete la model card con valores realmente obtenidos. Donde falte evidencia, escriba la limitación y cómo la reuniría, en lugar de afirmar cumplimiento.

## Esquema de consulta

![Expediente de una versión](../images/gobernanza.svg)

Fuente: elaboración propia.
