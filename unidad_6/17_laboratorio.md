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
