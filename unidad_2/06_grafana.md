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
