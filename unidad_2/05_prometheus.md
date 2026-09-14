# Prometheus e instrumentación del servicio

## Modelo de recolección

Prometheus consulta periódicamente `/metrics`. Este patrón pull separa el registro de observaciones de su almacenamiento temporal. Si la API deja de responder, la métrica `up` permite observar el fallo de scrape. Un `up=1` no garantiza que el modelo esté listo: por eso existe `bank_model_ready`.

Counter representa eventos acumulados; sus valores pueden reiniciarse cuando reinicia el proceso. Gauge representa un estado que sube o baja. Histogram acumula observaciones por buckets y permite aproximar cuantiles. No promediar percentiles ya calculados entre réplicas; combinar primero los buckets.

```python
from prometheus_client import Counter, Histogram
requests = Counter("demo_requests_total", "Peticiones", ["route", "status"])
latency = Histogram("demo_seconds", "Latencia", ["route"])
requests.labels("/predict", "200").inc()
latency.labels("/predict").observe(0.045)
```

## Cardinalidad
Cada combinación de etiquetas crea una serie. Un identificador por solicitud produciría crecimiento continuo. El proyecto usa plantilla de ruta y status, y agrupa rutas inexistentes como `unmatched`. No etiqueta con edad, payload, UUID ni ruta cruda. Los identificadores de predicción se guardan en un registro, fuera de Prometheus.

## PromQL útil

```promql
sum(rate(bank_http_requests_total[5m]))
sum(rate(bank_http_requests_total{status=~"5.."}[5m]))
histogram_quantile(0.95,
  sum by (le) (rate(bank_http_duration_seconds_bucket{route="/predict"}[5m])))
```

`rate` estima incremento por segundo considerando reinicios del contador. Para tasa de errores, dividir errores entre todas las solicitudes, manejando tráfico cero. Un panel vacío sin tráfico no equivale a un fallo. Para p95 elegir buckets próximos al objetivo: si todos los valores caen en un bucket enorme, la estimación será poco precisa.

El ejemplo usa un solo worker; las métricas en memoria de múltiples procesos requieren configuración multiproceso o un diseño distinto. Escalar workers sin revisar esto puede producir métricas parciales.

**Práctica:** provoque un 422 y consulte las series por status; luego visite una ruta inexistente y verifique que no aparece una nueva etiqueta por cada URL.

**Referencia:** [prácticas oficiales de instrumentación](https://prometheus.io/docs/practices/instrumentation/).
