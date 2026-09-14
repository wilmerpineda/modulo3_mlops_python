# Retraining programado y activado por evidencia

## Entrenar de nuevo no garantiza mejorar

Un calendario facilita mantenimiento, pero puede desperdiciar recursos si no llegan datos nuevos. Un trigger por drift puede reaccionar a datos defectuosos. Separar generación de candidato de decisión de despliegue permite automatizar trabajo sin entregar el control a una señal aislada.

El workflow semanal del laboratorio reentrena sobre el snapshot fijo: demuestra orquestación reproducible, no aprendizaje con nueva información. Para un sistema real habría que incorporar un snapshot nuevo, validar etiquetas, versionarlo y definir una ventana de entrenamiento. No usar la partición de prueba histórica repetidamente para optimizar candidatos.

```{mermaid}
flowchart LR
 A[Calendario o solicitud] --> B[Validar snapshot]
 B --> C[Entrenar candidato]
 C --> D[Comparar en validación]
 D --> E{Cumple controles}
 E -->|No| F[Conservar vigente]
 E -->|Sí| G[Revisión humana]
 G --> H[Promoción local]
 H --> I[Verificación y seguimiento]
```

## Comandos independientes

```powershell
poetry run python -m bank_ops.cli train --version candidate-v2 --kind candidate
poetry run python -m bank_ops.cli compare --candidate candidate-v2 --incumbent baseline-v1
```

Cada versión tiene su carpeta; repetir un nombre falla de forma explícita. Esta política evita sobrescribir evidencias. El workflow usa un runner limpio y conserva artefactos con el identificador de ejecución. El registro local está diseñado para un operador; coordinar escritores concurrentes requeriría bloqueo o una base transaccional.

## Datos y etiquetas
Antes de reentrenar, preguntar: ¿las etiquetas ya maduraron?, ¿cambió su definición?, ¿hay suficientes positivos?, ¿se introdujo sesgo de selección? Si solo se etiqueta a quienes el modelo decidió contactar, el próximo entrenamiento puede reforzar sus exclusiones. La automatización debe conservar esa advertencia en la evaluación.

**Práctica:** ejecute baseline y candidato, registre tiempo, métricas y tamaño. Escriba por qué un entrenamiento más costoso podría no justificar una actualización.

## Esquema de consulta

![Ciclo de actualización controlada](../images/ciclo.svg)

Fuente: elaboración propia.
