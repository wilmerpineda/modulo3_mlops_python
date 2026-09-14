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

<!-- MANUAL AVANZADO -->

## Capacidad, concurrencia y tiempo de respuesta

Throughput es trabajo completado por unidad de tiempo; concurrencia es trabajo en curso; latencia es tiempo por operación. Aumentar clientes concurrentes puede elevar throughput mientras existen recursos disponibles, pero después puede aumentar principalmente la espera. Observar cuatro clientes no demuestra que el servicio use cuatro núcleos ni que procese cuatro solicitudes a la vez en cada etapa.

Un cálculo de capacidad debe identificar la operación dominante. Validación, creación del DataFrame, transformación, estimación, serialización y escritura del log consumen recursos diferentes. En el ejemplo, el estimador vive en memoria y el endpoint es síncrono; FastAPI gestiona su ejecución conforme al modelo del servidor. Cambiar el endpoint a `async` sin cambiar operaciones bloqueantes no vuelve paralela una inferencia intensiva en CPU.

La relación $L=\lambda W$ expresa, bajo condiciones estables y fronteras consistentes, que el número medio de solicitudes en el sistema equivale a la tasa media de llegada multiplicada por el tiempo medio de permanencia. Si se completan 20 solicitudes por segundo y cada una permanece 0.2 segundos, la concurrencia media compatible es aproximadamente cuatro. No debe mezclarse un p95 con esa identidad de medias ni aplicarse como garantía durante una cola que crece sin límite.

## Un modelo de cola como herramienta de intuición

En una cola ideal M/M/1 con llegadas Poisson, tiempos de servicio exponenciales, un servidor y régimen estable, $W=1/(\mu-\lambda)$. Si el servidor ideal atiende 25 solicitudes por segundo, con 10 llegadas por segundo la media sería aproximadamente 0.067 segundos; con 20, 0.2; con 24, un segundo. La curva crece mucho cerca de saturación.

Ese modelo no describe exactamente la API de Python, que tiene planificación, múltiples recursos y tiempos de servicio no necesariamente exponenciales. Se usa para comprender por qué dimensionar al 100 % deja poco margen y puede generar latencias desproporcionadas. La capacidad real se mide bajo una carga representativa y con métricas de CPU, memoria, errores y tiempos. No se extrae de una fórmula sin validar sus supuestos.

```python
# Cálculo hipotético autónomo; no es un benchmark del servidor.
mu = 25.0
for arrival in [10, 20, 24]:
    print({"lambda": arrival, "rho": arrival/mu,
           "mean_seconds_mm1": 1/(mu-arrival)})
```

El margen también protege contra ráfagas, variaciones de payload y tareas de fondo. Dos cargas con la misma tasa pueden consumir recursos distintos si una requiere transformaciones más costosas. El ejemplo repite un payload para controlar parte de esa variación; sus resultados no representan toda mezcla posible de clientes.

## Interpretar el generador de carga entregado

`tools/load_test.py` crea clientes concurrentes mediante un pool de hilos, envía solicitudes a `127.0.0.1:8000` y conserva duración y estado de cada intento. Cada llamada usa una nueva petición de alto nivel de httpx, por lo que el costo del cliente y de conexión forma parte de la medición. El total de solicitudes dividido por el tiempo del ensayo es una tasa del experimento, no la capacidad máxima universal del servicio.

Con un número fijo de workers, cuando el servicio se ralentiza también baja la velocidad a la que el generador puede iniciar nuevas solicitudes. Es un patrón de carga cerrada: no reproduce necesariamente una fuente externa que continúe llegando a una tasa fija durante saturación. Esa distinción importa al estudiar acumulación de cola y timeouts. Para el curso se mantiene esta herramienta simple y se exige interpretar su alcance.

El campo `errors` cuenta cualquier estado distinto de 200, incluido cero para ciertos errores de transporte. Conviene separar HTTP 422, HTTP 503 y conexión fallida al revisar muestras. Un promedio de latencia sobre respuestas exitosas puede verse excelente si todas las solicitudes lentas terminaron en timeout y se excluyeron; conservarlas evita una conclusión sesgada.

```python
# Leer un ensayo real previamente generado desde proyecto_inicial.
import json
import numpy as np
from pathlib import Path
run = json.loads(Path("reports/load_test.json").read_text(encoding="utf-8"))
durations = np.array([row["seconds"] for row in run["samples"]])
print(dict(zip(["p50", "p95", "p99"], np.quantile(durations, [.5, .95, .99]))))
print({"attempts": len(durations), "errors": run["errors"]})
```

Con pocos intentos, p99 depende de muy pocas observaciones y debe interpretarse con cautela. El ensayo debe registrar calentamiento, duración, versión, recursos y actividad simultánea. Si se compara un worker con cuatro mientras cambia el modelo o se ejecuta entrenamiento en segundo plano, no se puede atribuir toda diferencia a concurrencia.

## Escalar el servicio y sus dependencias

El escalado vertical cambia recursos de una instancia. El horizontal añade instancias y necesita balanceo y coherencia del conjunto servido. Cada proceso puede cargar su propia copia del modelo, aumentando memoria. Una imagen pequeña en disco no implica poca memoria durante inferencia: objetos deserializados, buffers y transformaciones tienen otra representación. [Procesos de servidor en FastAPI](https://fastapi.tiangolo.com/deployment/server-workers/).

El proyecto usa un worker y un log local con lock de hilos. Ese lock no coordina procesos distintos. Antes de ampliar workers se necesita una estrategia de registro y métricas multiproceso; antes de ampliar réplicas, almacenamiento y etiquetado por instancia coherentes. Añadir un número a `--workers` sin revisar esas fronteras puede aumentar capacidad de CPU y reducir calidad de observabilidad o integridad de logs.

El modelo vigente también debe ser consistente. Una réplica que no se reinició puede servir otra versión mientras todas responden health 200. Un balanceador distribuiría decisiones diferentes sin que un gauge de disponibilidad lo denuncie. La liberación debe verificar versión por instancia o por conjunto de tráfico, según la arquitectura elegida.

## Resiliencia ante saturación

Timeouts limitan cuánto espera el cliente, pero no garantizan cancelar todo trabajo del servidor. Reintentos sin límite pueden aumentar carga durante un incidente y agravar la saturación. Backoff y dispersión temporal reducen sincronización, y un presupuesto de reintentos evita que cada solicitud original se multiplique indefinidamente. Las políticas deben considerar si repetir la operación tiene efectos secundarios.

En el ejemplo, inferir también escribe un evento con un identificador nuevo. Reintentar una llamada puede producir registros duplicados desde el punto de vista de intención del cliente, aunque los identificadores sean diferentes. Una clave idempotente y almacenamiento apropiado podrían resolver parte del problema, pero no se implementan en esta API docente. El cliente debe reconocer ese límite al interpretar conteos.

Una cola acotada o un rechazo temprano pueden proteger estabilidad y permitir recuperación. Devolver una predicción inventada cuando falta el modelo oculta indisponibilidad y puede causar decisiones incorrectas. Un fallback solo es válido si su significado, calidad y uso están definidos. [Tratamiento de sobrecarga en Google SRE](https://sre.google/sre-book/handling-overload/).

## Presupuesto con unidades y sensibilidad

Un modelo de costo debe separar servicio permanente, entrenamiento, almacenamiento, transferencia, observabilidad y operación humana. Con valores hipotéticos, dos instancias durante 720 horas a 0.05 unidades por hora cuestan 72; cuatro entrenamientos de dos horas a 0.20 cuestan 1.6; cincuenta GB a 0.02 cuestan 1. El subtotal de esos tres componentes es 74.6, antes de red y trabajo humano. No son precios de un proveedor.

Si el tráfico se duplica, el costo no necesariamente se duplica: puede existir capacidad ociosa, o puede superarse un umbral que exige otra instancia. Si se duplica retención de métricas, el almacenamiento puede aproximarse al doble bajo tasa constante, pero compresión y cardinalidad alteran el comportamiento real. El análisis debe mostrar supuestos y un rango, no un número exacto sin contexto.

Optimizar significa preservar objetivos con menos recursos o mejorar resultados dentro de un presupuesto. Reducir entrenamiento sin revisar frescura puede ahorrar cómputo y aumentar error. Eliminar logs reduce almacenamiento y dificulta investigar incidentes. Un candidato algo más preciso puede requerir tanta capacidad adicional que no sea la mejor opción operativa. La comparación incorpora esas consecuencias junto a métricas predictivas.

```{admonition} Taller de capacidad
:class: dropdown
Compare los ensayos con uno y cuatro clientes. Si throughput apenas aumenta y p95 sube, proponga al menos dos explicaciones y una medición que las distinga. Revise CPU, log local y limitación del generador antes de concluir que necesita más réplicas. Luego indique qué componentes del presupuesto cambiarían con cada solución.
```

El resultado esperado es una recomendación condicionada por evidencia: qué cuello de botella parece dominante, qué cambio se probará, cómo se medirá y qué límite de interpretación conserva el ensayo.
