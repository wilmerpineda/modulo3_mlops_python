# Laboratorio integral: observar, decidir y recuperar

## Recorrido verificable

Use los comandos desde la raíz del proyecto. Registre la salida de cada paso y evite mezclar el registro local con el del contenedor.

1. Compruebe el snapshot con `python -m bank_ops.data`.
2. Entrene y promueva el baseline según la guía de ambiente.
3. Inicie la API, consulte readiness y envíe una predicción desde Swagger.
4. Ejecute `python -m bank_ops.cli monitor --version baseline-v1` y abra los informes.
5. Inicie Compose, genere tráfico y observe el dashboard.
6. Entrene el candidato y compare sobre validación.
7. Justifique promoción o rechazo; haga el ensayo de recuperación.

## Promoción controlada sin prometer mejora

```powershell
poetry run python -m bank_ops.cli train --version replica-v2
poetry run python -m bank_ops.cli compare --candidate replica-v2 --incumbent baseline-v1
poetry run python -m bank_ops.cli promote --version replica-v2 --actor equipo --reason "Ensayo con réplica equivalente"
# Reinicie la API; compruebe replica-v2 en /ready.
poetry run python -m bank_ops.cli rollback --actor equipo --reason "Ensayo de recuperación"
# Reinicie y confirme baseline-v1.
```

Una réplica enseña el mecanismo; no se reporta como avance predictivo. El bosque candidato permite una comparación independiente, que puede terminar en rechazo. La suite docente además fuerza deterioro y comprueba que el gate lo bloquea.

## Etiquetas de vuelta
El registro `reports/predictions.jsonl` conserva identificadores reales. Cree un CSV con columnas `prediction_id,target` usando únicamente resultados simulados y declárelos como tales. No empareje automáticamente los targets del dataset con solicitudes no vinculadas.

```powershell
poetry run python -m bank_ops.cli labels --predictions reports/predictions.jsonl --labels data/labels_demo.csv
```

## Cierre
Compruebe versión activa, health, readiness y respuesta; conserve informe del incidente. Detenga contenedores con `docker compose down`. Los volúmenes se conservan: no usar `down -v` como limpieza rutinaria, porque elimina modelos y registros del laboratorio.

**Preguntas de salida:** ¿qué cambió?, ¿qué no puede inferirse?, ¿por qué el candidato es o no elegible?, ¿qué acción recuperó efectivamente el servicio?, ¿qué se haría diferente con usuarios reales?

<!-- MANUAL AVANZADO -->

## Antes de comenzar: dos recorridos y un mismo caso

El recorrido de estudio ejecuta notebooks y explora conceptos sin completar automáticamente la entrega. El recorrido de actividad integra servicio, CI, reportes y actualización después de resolver las tareas señaladas. Esta separación permite comprender la comparación de candidatos en el notebook 06 antes de implementar `lifecycle.compare`, sin incluir en el libro una solución terminada de A3-01.

Trabaje desde la raíz de `actividad_3/proyecto_inicial` para los comandos del paquete. Los notebooks se ejecutan desde el libro y localizan esa carpeta. Use un único registro por ensayo y anote si opera Python local o Compose. No mezcle artefactos de ambos para construir una historia que parezca continua: los volúmenes del contenedor y las carpetas locales son estados diferentes.

La primera promoción del baseline permite iniciar la API aunque el gate esté pendiente. Las promociones posteriores llaman compare y fallarán con `NotImplementedError` hasta completar A3-01. A3-02 exige demostrar protección y recuperación; A3-03 exige pytest en CI. Esa condición debe revisarse antes de ejecutar la secuencia completa, porque el propósito del starter es que el equipo implemente esas capacidades.

## Punto de control 1: identificar el experimento

Registre revisión de código, Python, lock y huella de datos. Ejecute la validación del snapshot y conserve su resultado. Revise que duration, age y day no formen parte de FEATURES y que la partición preserve el orden definido. No se requiere afirmar que ese orden reconstruye todas las fechas o identifica personas: el informe debe repetir la limitación del caso.

```powershell
poetry run python --version
poetry run python -m bank_ops.data
poetry run pytest -q
```

En el estado inicial, una prueba está omitida deliberadamente. El resultado esperado al finalizar la actividad es que esa omisión haya desaparecido y sus comprobaciones existan. Conservar el número de tests ayuda a detectar omisiones, pero se debe revisar también qué comportamientos cubren. Una suite con más tests puede seguir sin comprobar versión HTTP después del rollback.

Si la huella falla, identifique si cambió el contenido, separador o finales de línea. No recalcule el manifiesto para eliminar el error sin investigar. Si falla importación, compruebe que el intérprete corresponde al entorno Poetry del proyecto y no a otro Python instalado. Esos diagnósticos son más útiles que repetir comandos al azar.

## Punto de control 2: baseline y servicio local

Entrene una versión nueva si el nombre propuesto ya existe. Las versiones inmutables conservan evidencia; la repetición de un comando no debería sobrescribir un resultado anterior. Si desea usar un baseline ya existente, compruebe su manifiesto y declare esa reutilización. El servidor debe cargar el registro que se está preparando.

```powershell
poetry run python -m bank_ops.cli train --version baseline-v1
poetry run python -m bank_ops.cli promote --version baseline-v1 --actor equipo --reason "Inicialización del laboratorio"
poetry run uvicorn bank_ops.api:app --host 127.0.0.1 --port 8000
```

La tercera instrucción mantiene un proceso activo: use otra terminal para las consultas. Si el puerto está ocupado, identifique el proceso del laboratorio que ya lo utiliza; no termine servicios ajenos. Confirme health, readiness y metadatos. Desde Swagger envíe una entrada válida o use el siguiente fragmento Python, que toma exclusivamente features del snapshot.

```python
# En otra terminal, desde proyecto_inicial y con la API en 8000.
import httpx
from bank_ops.data import load
from bank_ops.config import FEATURES
payload = load().iloc[0][FEATURES].to_dict()
response = httpx.post("http://127.0.0.1:8000/predict", json=payload, timeout=10)
response.raise_for_status()
prediction = response.json()
print(prediction)
```

La respuesta debe incluir identificador, probabilidad, decisión, umbral y versión. Guarde la relación entre esa solicitud y su respuesta si luego simulará etiquetas. No asigne automáticamente el primer target del CSV a cualquier identificador del log: sin correspondencia de entradas, esa unión sería falsa aunque el formato sea correcto.

## Punto de control 3: monitoreo y evidencia de datos

Ejecute el comando monitor para la versión elegida. Revise reportes estable, shift y degraded, anotando cuáles entradas fueron modificadas y si cambió Y. La comparación estable usa dos subconjuntos de validation; el reporte final de test tiene otro propósito y no debe reutilizarse para ajustar el gate. Si se decide explorar test durante estudio, deje claro que ya no puede presentarse como evaluación final intacta de futuras decisiones.

La evidencia mínima es una tabla interpretada: escenario, medida o métrica, referencia, tamaño, conclusión y limitación. Una captura de Evidently sin identificar la ventana no permite reconstruir el análisis. El agregado puede indicar ausencia de drift global mientras dos columnas sí cambian; explique la regla de conteo y por qué una feature crítica puede exigir revisión aunque el agregado no se active.

Para etiquetas tardías, cree resultados simulados solo para identificadores conocidos y declare el mecanismo de observación. Calcule cobertura por versión y compare resultados con los notebooks. La ausencia de etiqueta no se transforma en negativo. Si un lote tiene una sola clase, AUC y AP pueden quedar sin definición en la función del proyecto; conservar esa salida es parte de reportar honestamente.

## Punto de control 4: observabilidad y alerta

Detenga la API local si va a iniciar Compose en el mismo puerto. Compruebe el motor Docker antes de construir. Después revise que los tres servicios estén activos y que Prometheus consulte el target correcto. Los archivos JSON del dashboard y las reglas están versionados; no necesita reconstruir manualmente cada panel para comenzar.

```powershell
docker info
docker compose up --build -d
docker compose ps
poetry run python tools/load_test.py --requests 300 --workers 1
Copy-Item reports/load_test.json reports/load_test_w1.json
poetry run python tools/load_test.py --requests 300 --workers 4
Copy-Item reports/load_test.json reports/load_test_w4.json
```

Las copias conservan ambos ensayos; si esos nombres ya existen, use otros identificadores de ejecución para no perder evidencia. El generador apunta a la API publicada en 8000, pero sus JSON se escriben en el proyecto local. El log de predicciones de la API en contenedor permanece en su volumen. Esa diferencia es esperada y debe documentarse.

Para el incidente, detenga solo api y observe `up` en Prometheus. Espere la persistencia de la regla, registre tiempos y restaure. Compruebe después una predicción válida. El ensayo no se considera realizado si el motor falla antes de iniciar los servicios. Puede conservarse el diagnóstico como pendiente, pero no reemplazarlo con una captura dibujada. El informe de preparación del material distingue esas situaciones.

## Punto de control 5: candidato y decisión

Después de completar A3-01, entrene el bosque con un nombre disponible y compare contra el vigente. Conserve el JSON completo y explique cada condición: dirección, diferencia y tolerancia. Si una condición falla, no cambie el puntero ni modifique la política para favorecer al candidato. La decisión puede ser rechazar, investigar o producir otro experimento, conservando la validación como conjunto de selección.

El notebook 06 añade comparación pareada y análisis de costo del entrenamiento. Es una ayuda para interpretar incertidumbre, no un reemplazo de la tarea. El informe debe distinguir mejora puntual, elegibilidad bajo tolerancias y aprobación integral. Si ambos modelos tienen recall cero al umbral inicial, comunique ese límite aunque una condición relativa pase.

La promoción de una réplica equivalente sirve para ensayar el mecanismo cuando el bosque es rechazado. Entrene la réplica con otra versión, declare su propósito y verifique que la comparación admite equivalencia. No la presente como un avance predictivo. Esa honestidad evita que la actividad premie fabricar mejoras en lugar de operar correctamente.

## Punto de control 6: transición y recuperación verificadas

Ejecute promoción y rollback en el mismo registro que utiliza la API. Si está en Compose, use `docker compose exec api python -m bank_ops.cli ...` y reinicie ese servicio. Si está en local, reinicie el proceso uvicorn correspondiente. Consultar un endpoint distinto puede producir resultados aparentemente contradictorios aunque ambos entornos estén bien configurados.

Conserve tres respuestas HTTP: antes de promover, después de promover y después de revertir. Cada una debe informar la versión esperada y acompañarse de una predicción válida. Conserve además el puntero y registro de acciones. Las dos fuentes responden preguntas diferentes: qué se configuró y qué se ejecutó. Si divergen, no cierre el ensayo como exitoso.

Revise qué ocurre si no existe antecesor, si la versión ya está activa o si el artefacto es incompatible. Esos casos se estudian en temporales mediante tests; no es necesario corromper el registro válido de la demostración. La recuperación debe proteger la evidencia anterior y permitir explicar el estado final.

## Punto de control 7: CI y entrega en equipo

Cree el repositorio de actividad con proyecto_inicial como raíz, complete A3-03 y conserve una ejecución fallida deliberada y su reparación. Compruebe que los logs muestran pytest, no solo compilación. Ejecute el retraining manual después de completar compare y revise artefactos. Un workflow programado configurado pero nunca ejecutado no es evidencia de automatización comprobada.

Cada integrante aporta el PR y revisión exigidos por la actividad. El informe de dos o tres páginas prioriza decisiones, evidencia y límites; enlaza reportes extensos en lugar de copiarlos completos. La demostración de cinco a siete minutos debe mostrar el recorrido esencial: servicio, observabilidad, decisión y recuperación. Las ampliaciones estadísticas son recursos de estudio y no añaden entregables obligatorios.

Antes de terminar, confirme que el estado final es intencional y que otro integrante puede reproducirlo. Detenga los servicios del ensayo con `docker compose down` cuando corresponda; no use eliminación de volúmenes como limpieza rutinaria. Guarde las evidencias con identificadores claros y revise que no se incluya la solución docente en el repositorio público del equipo.

## Criterio de cierre del laboratorio

El recorrido está completo cuando otra persona puede responder con evidencia qué versión está sirviendo, de qué datos procede, qué señales se observaron, por qué se aceptó o rechazó una actualización y cómo se recuperó el servicio. Las métricas no tienen que ser favorables; las conclusiones sí deben corresponder a los resultados.

```{admonition} Revisión final antes de presentar
:class: dropdown
Si solo dispone de capturas, compruebe si incluyen versión, tiempo y consulta. Si solo dispone de JSON, compruebe si existe una explicación de sus límites. Si el candidato fue rechazado, verifique que esa decisión dejó el vigente intacto. Si el dashboard no pudo ejecutarse, declare el bloqueo concreto y qué comprobaciones permanecen pendientes. La calidad de la entrega depende de coherencia y reproducibilidad, no de ocultar resultados incómodos.
```
