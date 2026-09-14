# Grafana, dashboards y alertas accionables

## Dashboard como herramienta de diagnóstico

El dashboard se provisiona desde JSON. Incluye tráfico, latencia p95, errores 5xx, readiness, predicciones por clase y disponibilidad del target. Tener su definición en Git permite revisar qué se mide y reconstruirlo sin configuración manual.

El flujo de datos es API → Prometheus → Grafana. Si una curva no aparece, comprobar primero `/metrics`, luego el target y la consulta en Prometheus, y por último la fuente del panel. Cambiar colores no corrige una consulta sin datos.

```powershell
docker compose up --build -d
poetry run python tools/load_test.py --requests 300 --workers 4
```

Abra Grafana, busque **Bank Ops · Módulo 3**, espere varios scrapes y ajuste el rango temporal. El test genera tráfico real; un solo lote breve puede quedar fuera de una ventana de consulta posterior.

## Alertas

Las reglas entregadas viven en Prometheus y se visualizan en su página de alertas. No se incluye envío automático de correos ni Alertmanager. Una regla pasa de inactiva a pendiente y después a activa cuando la condición persiste durante `for`.

| Alerta | Condición | Respuesta inicial |
|---|---|---|
| API no disponible | `up == 0` por un minuto | Revisar proceso, puerto y red |
| Modelo no listo | gauge en cero por un minuto | Revisar artefacto y puntero |
| Latencia alta | p95 > 0.5 s durante dos minutos | Revisar carga, CPU y tiempos |

Una buena alerta identifica dueño, severidad y runbook. Si nadie puede actuar, es información para un dashboard, no necesariamente una notificación urgente. El tiempo de persistencia reduce ruido, pero retrasa la detección; debe corresponder al impacto.

## Ensayo de incidente
Detenga solo la API con `docker compose stop api`, mantenga Prometheus y Grafana y observe `up`. Registre hora del fallo, primera observación y activación. Restaure con `docker compose start api` y verifique recuperación. No interprete la última predicción conservada como actividad nueva.

**Ejercicio:** diseñe una regla de errores 5xx que no dispare con una única petición fallida cuando el servicio casi no recibe tráfico. Justifique volumen mínimo, ventana y persistencia.

<!-- MANUAL AVANZADO -->

## Diseñar el dashboard alrededor de decisiones

Un dashboard operativo debe permitir contestar preguntas en orden: ¿hay tráfico?, ¿podemos observar el servicio?, ¿puede atender?, ¿cómo se comporta bajo esa carga?, ¿hay un cambio que exige actuar? Empezar por veinte gráficos de distribución puede distraer de una caída de la API. La organización del panel forma parte de la capacidad de diagnóstico, no solo de su apariencia.

Para Bank Marketing conviene una primera fila con disponibilidad del target, readiness, tasa de solicitudes y fracción de errores. Una segunda fila presenta latencia y conteos por clase predicha. Los reportes de drift y desempeño con etiquetas se consultan con su propia fecha de corte, porque no se actualizan al ritmo del servicio. Un mismo tablero puede enlazarlos, pero debe evitar que una métrica de ayer parezca una medición de los últimos cinco minutos.

Cada panel necesita unidad, descripción, consulta, rango y significado de ausencia. Un valor de 0.25 puede representar segundos, proporción o cantidad: el título y la unidad deben eliminar esa ambigüedad. Los colores deben corresponder a objetivos explícitos, no a valores por defecto. Una línea roja en 0.5 segundos solo tiene significado si el equipo entiende qué ruta, población y cuantil se comparan.

## Provisionamiento y cambios reproducibles

La configuración del proyecto incluye una fuente Prometheus y un dashboard JSON. La fuente apunta al nombre del servicio dentro de la red Compose, no al `localhost` del navegador. Dentro del contenedor Grafana, `localhost:9090` designaría al propio contenedor y no al servicio Prometheus. Esta distinción explica muchos paneles vacíos en entornos locales.

El provisionamiento permite reconstruir la vista desde Git. Si se edita en la interfaz, debe exportarse y revisarse la definición antes de considerar persistente el cambio. Un dashboard modificado solo en un volumen local no acompaña automáticamente al repositorio del equipo. Conviene revisar diferencias en consultas, unidades y umbrales; los cambios de posición visual no son equivalentes a cambios de significado.

El material usa Grafana 11.6.0 fijado en Compose. Las pantallas de documentación reciente pueden variar; el contrato importante es el JSON provisionado y la fuente configurada. La lectura anónima está limitada al laboratorio local con puertos en loopback. Una publicación de ese dashboard en otro entorno necesitaría revisar autenticación y exposición; no se solicita desplegarlo públicamente para esta actividad. [Documentación de provisionamiento](https://grafana.com/docs/grafana/latest/administration/provisioning/).

## Un procedimiento para «no hay datos»

Primero genere solicitudes reales y consulte `/metrics` directamente. Después compruebe el target `bank-api` y una consulta simple en Prometheus. Si allí existen series recientes, pase a la fuente de datos de Grafana y finalmente al panel. Esta secuencia localiza la frontera de fallo. Cambiar consultas avanzadas antes de confirmar que existe tráfico suele consumir tiempo sin producir evidencia.

Un contador puede no tener todavía una combinación de etiquetas si nunca ocurrió ese evento. Una tasa necesita suficientes muestras y un rango temporal que las contenga. Si se ejecutó una carga hace veinte minutos y el panel muestra los últimos cinco, la ausencia de actividad puede ser correcta. También hay que distinguir un filtro de ruta incorrecto, un nombre de métrica distinto y una fuente que apunta a otro proyecto Compose.

| Síntoma | Hipótesis inicial | Comprobación concreta |
|---|---|---|
| Todos los paneles vacíos | Fuente o target incorrecto | Consultar `up` en Prometheus y en Grafana |
| Tráfico visible, p95 vacío | Falta de observaciones o filtro | Consultar count y buckets de `/predict` |
| Tasa de error muy variable | Volumen bajo | Revisar increase del denominador |
| Readiness 1, versión inesperada | Proceso no reiniciado | Consultar `/model/metadata` |
| Predicciones históricas, API caída | Datos conservados | Revisar tiempo de muestra y `up` |

## SLI, SLO y presupuesto de error

Un SLI es una medición definida; un SLO fija un objetivo para esa medición durante un periodo. Un acuerdo contractual puede añadir obligaciones externas, pero no todo objetivo docente es un SLA. En este laboratorio podría estudiarse «proporción de solicitudes correctas» y, por separado, «proporción bajo 500 ms», reconociendo la limitación de instrumentación para su intersección. [Objetivos de servicio en Google SRE](https://sre.google/sre-book/service-level-objectives/).

Con un objetivo hipotético de 99 % de éxito sobre 100 000 solicitudes elegibles, el presupuesto de error es 1 000 fallos. Si se consumen 300, queda 70 % de ese presupuesto. El cálculo necesita definir elegibilidad: errores de cliente, solicitudes inválidas, mantenimiento y reintentos no pueden incluirse o excluirse según convenga después del incidente. Un objetivo por solicitudes no es equivalente a uno por minutos de disponibilidad.

La tasa de consumo o burn rate compara la fracción observada de errores con la fracción permitida. Con presupuesto 1 % y error observado 5 %, el consumo relativo es 5. Si ese régimen persistiera, agotaría el presupuesto más rápido que el objetivo. Una ventana corta detecta deterioro rápido; una larga evita alarmas por picos breves. El material presenta el razonamiento, sin incorporar una política industrial completa de múltiples ventanas al starter.

## Alertas con volumen y persistencia

Una proporción del 50 % basada en dos solicitudes no tiene el mismo peso que la misma proporción sobre diez mil. Para una alerta educativa de errores se puede combinar fracción superior a 5 %, al menos 100 solicitudes en cinco minutos y persistencia de dos minutos. Los valores son hipótesis de diseño para experimentar, no compromisos reales del servicio.

```promql
(
  (
    sum(rate(bank_http_requests_total{route="/predict",status=~"5.."}[5m]))
    or vector(0)
  )
  /
  clamp_min(sum(rate(bank_http_requests_total{route="/predict"}[5m])), 0.000001)
  > 0.05
)
and
(sum(increase(bank_http_requests_total{route="/predict"}[5m])) >= 100)
```

Esta expresión es un ejemplo para una regla adicional, no una regla ya activa del proyecto. Su condición de volumen deja sin evaluar proporcionalmente periodos con muy poco tráfico; por eso debe coexistir con disponibilidad y pruebas de salud. El campo `for: 2m` se añade en YAML y exige persistencia de la condición. El tiempo total de detección incluye scrape, evaluación, acumulación de ventana y persistencia: no debe confundirse con exactamente dos minutos desde el primer fallo.

## Runbook de caída y recuperación

Antes del ensayo, confirme que la API funciona y que Prometheus la recolecta. Anote hora UTC y versión, genere tráfico y conserve una captura inicial. Detenga únicamente `api`, observe el target y espere la condición de la regla existente. Mantener Prometheus y Grafana activos permite que el fallo sea visible. Si se detiene toda la pila, se elimina también el observador y el experimento responde otra pregunta.

Después restaure el servicio y confirme `/health`, `/ready`, versión y una predicción real. El hecho de que `up` vuelva a uno demuestra recolección, no necesariamente que el modelo esperado esté sirviendo. Registre inicio, detección, acción, recuperación técnica y cierre de impacto. Si faltan etiquetas, el impacto predictivo puede continuar pendiente aunque el servicio vuelva a responder.

La regla de readiness y la regla de target caído se complementan. Cuando la API está apagada, el gauge no se actualiza; no se debe exigir que aparezca mágicamente en cero. Si está viva pero no pudo cargar modelo, el endpoint de métricas existe y el gauge puede comunicar esa condición. Una alarma requiere entender cómo falla también su propia fuente de observación.

## Fatiga de alertas y revisión posterior

Una alerta accionable identifica condición, severidad, responsable, primera comprobación y criterio de cierre. Si toda señal estadística llama al mismo operador inmediatamente, la atención se consume en eventos que quizá no exijan intervención. Separar incidentes de servicio de hallazgos de calidad para revisión permite asignar tiempos de respuesta distintos sin ignorar ninguno.

Después del ensayo evalúe si la alerta permitió decidir. Una captura roja es evidencia de activación, pero falta saber si llegó tarde, si dependía de una consulta equivocada o si permaneció activa después de recuperar el servicio. Revise también falsos positivos: errores intencionales del cliente pueden generar 422 sin que exista una caída del backend. Su aumento merece diagnóstico de integración, con otra severidad y otro responsable.

```{admonition} Ejercicio de profundización opcional
:class: dropdown
Diseñe dos paneles para el mismo servicio: uno para quien atiende incidentes y otro para quien revisa calidad semanal. El primero necesita señales recientes, volumen y estado; el segundo necesita cohortes, maduración y comparación por versión. Justifique qué información compartirían y qué ventanas mantendría separadas. No es necesario añadir herramientas nuevas ni modificar la rúbrica.
```

La evidencia de Grafana debe proceder de una ejecución real. Si el motor Docker falla antes de iniciar la pila, conserve el diagnóstico y declare el ensayo pendiente; una imagen ilustrativa del flujo no sustituye una captura de la alerta funcionando.
