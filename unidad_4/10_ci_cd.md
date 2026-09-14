# CI, entrega continua, despliegue y entrenamiento

## Separar responsabilidades

Integración continua ejecuta verificaciones al integrar cambios pequeños. Entrega continua produce un artefacto desplegable y conserva una decisión explícita de liberación. Despliegue continuo automatiza también la liberación cuando pasan los controles. Entrenamiento continuo genera candidatos cuando se activan condiciones de datos o calendario.

Un pipeline verde no prueba que el modelo sea útil: solo que pasó los controles implementados. Un entrenamiento exitoso tampoco implica autorización para servir el resultado. Por eso el workflow de candidato termina guardando evidencia, sin promover automáticamente.

```{mermaid}
flowchart LR
 A[Rama y PR] --> B[Pruebas de datos y código]
 B --> C[Build y smoke test]
 C --> D[Artefacto entregable]
 D --> E[Revisión de liberación]
 E --> F[Despliegue local]
 F --> G[Monitoreo]
 G --> H[Candidato]
 H --> E
```

## Qué versionar
Código, contratos, configuración, definición del dashboard, reglas de alerta y workflows son texto revisable. El pequeño snapshot docente se conserva con checksum para que CI no dependa de UCI. En grandes volúmenes, usar almacenamiento de objetos y manifiestos o herramientas de versionado de datos; no añadir gigabytes al historial Git.

## Diseño de una revisión
Cada PR describe problema, cambio, evidencia y limitaciones. Las pruebas rápidas fallan antes del build costoso. Integrar cambios pequeños facilita revertir. La definición de terminado exige que otra persona reproduzca el README, no solo que el autor muestre una captura.

La solución entrega la imagen como artefacto de Actions después de integrar en `main`. El entorno local recibe y ejecuta el artefacto mediante un paso explícito. Un runner alojado en GitHub no controla el Docker de la computadora del estudiante.

**Ejercicio:** clasifique descargar datos nuevos, validar esquema, entrenar, construir imagen, aprobar y reiniciar el servicio dentro de CI, entrega, despliegue o entrenamiento. Algunas acciones pueden aparecer en más de un flujo; justifique su ubicación.

## Esquema de consulta

![De la revisión a la entrega](../images/ci_cd.svg)

Fuente: elaboración propia.
