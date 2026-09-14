# Escalabilidad, resiliencia y costos

## Medir antes de escalar

El tiempo por petición depende de validación, transformación, inferencia, serialización y registro. Aumentar réplicas ayuda si el cuello de botella permite paralelismo; no resuelve una fuente externa lenta o un lock global. El servicio docente carga el modelo al inicio para no deserializarlo en cada predicción.

Escalado vertical añade recursos a una instancia; horizontal distribuye solicitudes. El segundo exige balanceo, consistencia de versiones, almacenamiento apropiado y observabilidad por réplica. Los archivos locales y métricas de un worker del ejemplo son límites explícitos para esa extensión.

## Resiliencia
Liveness pregunta si el proceso vive; readiness si puede atender correctamente. Un orquestador puede retirar de tráfico una instancia no lista sin reiniciarla continuamente. Retries necesitan límites y backoff; repetir una operación con efectos puede duplicarlos. Para inferencia, un identificador idempotente ayudaría a evitar doble registro, pero el ejemplo genera uno nuevo por llamada.

Un fallback debe tener significado de negocio. Devolver cero cuando falta el modelo oculta un fallo y altera decisiones. El proyecto devuelve 503 para que el cliente pueda reconocer indisponibilidad.

## Experimento de carga

```powershell
poetry run python tools/load_test.py --requests 300 --workers 1
poetry run python tools/load_test.py --requests 300 --workers 4
```

Conservar ambos resultados con nombres distintos antes de repetir: el comando escribe `load_test.json`. Comparar throughput, errores y percentiles con CPU y memoria. El cliente abre conexiones por solicitud, por lo que incluye costo de cliente y conexión; no interpretarlo como benchmark puro del estimador.

## Costos
Costo mensual aproximado = horas de cómputo × tarifa + almacenamiento + transferencia + observabilidad + operación humana. Las cifras deben rotularse como supuestos cuando no proceden de una cotización. Optimizar frecuencia de entrenamiento, retención de métricas y tamaño del modelo puede ahorrar más que cambiar proveedor.

Ejemplo hipotético: 40 horas de entrenamiento a 0.20 unidades/hora cuestan 8 unidades; reducir a 10 horas cuesta 2. No representa una tarifa real. La reducción solo sirve si conserva resultados y tiempos de actualización aceptables.

**Ejercicio:** proponga un presupuesto con unidades, supuestos y sensibilidad al doble de tráfico. Incluya el costo de retener métricas con demasiadas etiquetas.
