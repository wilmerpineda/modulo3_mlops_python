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

<!-- MANUAL AVANZADO -->

## Del evento HTTP a una serie temporal

Prometheus consulta periódicamente un endpoint que expone valores. La API incrementa contadores y observa duraciones cuando procesa solicitudes; el servidor de métricas registra muestras de esos acumulados. Una muestra no representa una solicitud individual. Conservar esa distinción evita interpretar una línea plana de contador como ausencia histórica de tráfico o sumar muestras de un contador como si fueran eventos independientes.

El proyecto usa un `CollectorRegistry` por instancia de aplicación. Esto permite crear aplicaciones de prueba sin colisiones con métricas registradas anteriormente en el proceso. Las métricas se publican con el formato de la biblioteca cliente y la ruta `/metrics` se excluye de la instrumentación HTTP del ejemplo. De lo contrario, los propios scrapes añadirían tráfico y latencia a las métricas que se pretende interpretar.

Las etiquetas son dimensiones. `route="/predict"` agrupa solicitudes del mismo endpoint; `status="200"` separa resultados HTTP. El identificador de predicción pertenece al registro de eventos, no a una etiqueta de Prometheus. Si se añade como etiqueta, cada solicitud crea otra serie, lo cual eleva cardinalidad, memoria y costo de consulta. La utilidad de una dimensión debe evaluarse antes de exponerla.

## Elegir el instrumento adecuado

Un counter describe eventos acumulados desde el inicio del proceso: solicitudes o predicciones por clase. Puede reiniciarse al reiniciar la aplicación. Un gauge representa un estado que puede subir y bajar, como `bank_model_ready`. Un histograma clásico cuenta observaciones por límites acumulados, además de conservar suma y cantidad. El proyecto usa histogramas clásicos; no se deben copiar consultas para histogramas nativos y esperar que funcionen sin adaptar la instrumentación.

| Instrumento local | Pregunta que responde | Lectura incorrecta |
|---|---|---|
| `bank_http_requests_total` | Cuántas solicitudes ha procesado la instancia | Su valor actual es solicitudes por segundo |
| `bank_model_ready` | Si el proceso cargó un modelo al iniciar | Demuestra que el modelo sigue siendo útil |
| `bank_http_duration_seconds_bucket` | Cuántas duraciones quedaron bajo cada límite | Cada bucket contiene solo su intervalo |
| `bank_predictions_total` | Cuántas decisiones 0/1 produjo la API | Equivale a frecuencia real de suscripciones |

El gauge de readiness del proyecto se fija durante el arranque. Si después se cambia `current.json`, el proceso no recarga el modelo automáticamente ni vuelve a validar su utilidad. La comprobación de versión HTTP sigue siendo necesaria. Asimismo, `up` mide si Prometheus logró consultar el target; no verifica todos los endpoints ni sustituye una prueba funcional de predicción.

## Construir consultas desde unidades

Para tráfico reciente, aplicar `rate` a cada counter y luego agregar. La función considera reinicios dentro de la ventana; sumar contadores de varias instancias antes de estimar la tasa puede ocultar reinicios individuales. Una ventana de cinco minutos ofrece varias muestras con el intervalo del laboratorio y suaviza ruido; para una investigación más rápida puede usarse otra ventana, verificando que haya suficientes scrapes. [Funciones de PromQL](https://prometheus.io/docs/prometheus/latest/querying/functions/).

```promql
sum(rate(bank_http_requests_total{route="/predict"}[5m]))
```

La unidad es solicitudes por segundo. Para estimar solicitudes del intervalo se utiliza `increase` y se declara que la estimación depende de muestras y extrapolación, no de un log exacto de eventos. Una métrica de facturación requeriría garantías adicionales que esta instrumentación no proporciona.

```promql
sum(increase(bank_http_requests_total{route="/predict"}[5m]))
```

Para errores, numerador y denominador deben representar la misma población. Dividir errores de todas las rutas por tráfico de `/predict` produciría un porcentaje sin significado. Un fallo de validación 422 no es un fallo 5xx, aunque pueda indicar un problema serio de integración del cliente. Conviene observarlos por separado.

```promql
(
  sum(rate(bank_http_requests_total{route="/predict",status=~"5.."}[5m]))
  or vector(0)
)
/
clamp_min(sum(rate(bank_http_requests_total{route="/predict"}[5m])), 0.000001)
```

El cero del numerador permite representar ausencia de series 5xx en un panel simple. No debe utilizarse para convertir un target desaparecido en servicio saludable: mostrar `up` y volumen junto a esa razón es parte del contrato del panel. El pequeño piso evita división numérica por cero, pero no convierte tráfico insuficiente en una estimación estadísticamente estable.

## Histogramas y percentiles con interpretación

La API observa segundos con límites desde 0.005 hasta 5, más el bucket infinito añadido por la biblioteca. Cada observación incrementa todos los buckets cuyo límite la contiene. Por eso un bucket con `le="0.5"` incluye todas las solicitudes de medio segundo o menos, no solo las que están entre 0.25 y 0.5. Para reconstruir intervalos se restarían acumulados vecinos.

```promql
histogram_quantile(
  0.95,
  sum by (le) (
    rate(bank_http_duration_seconds_bucket{route="/predict"}[5m])
  )
)
```

La consulta agrega buckets compatibles y estima el cuantil. No se promedian p95 individuales: el percentil de una mezcla no es la media de sus percentiles. La precisión depende de los límites disponibles y de dónde caen las observaciones. Si un objetivo exige 500 ms, disponer de un límite 0.5 permite calcular directamente la fracción que lo satisface. [Histogramas en Prometheus](https://prometheus.io/docs/practices/histograms/).

```promql
sum(rate(bank_http_duration_seconds_bucket{route="/predict",le="0.5"}[5m]))
/
sum(rate(bank_http_duration_seconds_count{route="/predict"}[5m]))
```

Esta fracción incluye las solicitudes instrumentadas de la ruta, no exclusivamente respuestas correctas. El histograma local no tiene etiqueta de estado. Por tanto, combinar disponibilidad y latencia como un único SLI de «respuestas correctas y rápidas» requeriría instrumentación adicional o eventos enlazables. Multiplicar ambas fracciones sería injustificado sin conocer su dependencia.

## Qué duración se está midiendo

El middleware usa un reloj monotónico mediante `perf_counter`, apropiado para diferencias de tiempo. Su medición abarca el procesamiento observado por la aplicación; no incluye necesariamente toda la espera en un proxy, la red del cliente o la recepción completa de una respuesta transmitida. La API del laboratorio produce JSON pequeño y no streaming, pero esa frontera debe seguir documentada.

La prueba de carga mide desde el cliente y añade apertura de conexiones y planificación del generador. Es esperable que sus percentiles difieran de los del servidor. Esa diferencia puede servir como pista sobre red o cliente, aunque no constituye una descomposición exacta si las ventanas y las solicitudes no están alineadas. No se debe seleccionar el número menor y llamarlo «la latencia real».

## Cardinalidad como presupuesto

Con cinco rutas y seis estados posibles, un counter podría exponer hasta treinta combinaciones observadas. Añadir versión de modelo, réplica y región multiplica posibilidades. Un histograma agrega además series por bucket, suma y count. La cardinalidad efectiva depende de combinaciones existentes, pero un diseño que permite identificadores sin límite carece de un máximo operativo razonable.

Para analizar versiones, una solución puede agregar una métrica informativa de versión por instancia y unirla cuidadosamente al consultar, o limitar las versiones expuestas. No se añade esa complejidad al ejemplo de un worker. En una ampliación con varios workers, usar simplemente el mismo archivo JSONL y registries independientes detrás de un balanceador no produce métricas globales fiables. Se necesita una estrategia de recolección y almacenamiento coherente.

## Práctica de diagnóstico

Desde una terminal mantenga la API activa; en otra consulte `/metrics` antes y después de varias predicciones. Observe qué series aparecen únicamente después de usar una combinación de etiquetas. A continuación consulte el target en Prometheus y compare el tiempo de la última muestra con la hora actual. Una aplicación que expone datos correctamente puede no estar siendo recolectada por un error de red o configuración.

```{admonition} Caso para discutir
:class: dropdown
El dashboard muestra cero errores, pero `up` pasó a cero. ¿Es válido informar disponibilidad perfecta? No: la ausencia de nuevos errores puede deberse a ausencia de recolección. La señal de observabilidad debe distinguir cero eventos, tráfico insuficiente y pérdida del target. El diseño debe conservar esos estados, aunque el panel de porcentaje use un valor de respaldo para su numerador.
```

La evidencia de esta práctica debe incluir una consulta, sus unidades, la población filtrada y la ventana. Con esos cuatro elementos, otra persona puede evaluar si la interpretación corresponde a la medición; una captura sin consulta ni rango temporal aporta mucho menos.
