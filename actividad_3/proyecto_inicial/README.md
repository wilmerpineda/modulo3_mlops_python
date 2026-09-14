# Bank Ops — Módulo 3

Python 3.11 y Poetry 2.1.3. Ejecutar desde esta carpeta; la instalación necesita red, las pruebas usan snapshot local.

```powershell
poetry env use 3.11
poetry install
poetry run python -m bank_ops.data
poetry run python -m bank_ops.cli train --version baseline-v1
poetry run python -m bank_ops.cli promote --version baseline-v1 --actor equipo --reason "Bootstrap educativo"
poetry run pytest -q
poetry run uvicorn bank_ops.api:app --host 127.0.0.1 --port 8000
```

No repetir un nombre de versión existente. Consulte `/docs`, `/health`, `/ready`, `/model/metadata` y `/metrics`. En otra terminal:

```powershell
poetry run python -m bank_ops.cli monitor --version baseline-v1
poetry run python -m bank_ops.cli train --version candidate-v2 --kind candidate
poetry run python -m bank_ops.cli compare --candidate candidate-v2 --incumbent baseline-v1
```

El proyecto inicial requiere completar TAREAS.md antes de comparar y promover nuevas versiones. Un rechazo es válido. La API carga al inicio: reiniciar y comprobar versión después de promover o revertir.

## Docker y observabilidad

Detener la API anterior si ocupa 8000 e iniciar Docker Desktop.

```powershell
docker compose up --build -d
docker compose ps
poetry run python tools/load_test.py --requests 300 --workers 4
```

Grafana: http://localhost:3000 ; Prometheus: http://localhost:9090 . Dashboard Bank Ops · Módulo 3. Las alertas viven en Prometheus, sin notificaciones externas. Los volúmenes son otro registro distinto del de Python local:

```powershell
docker compose exec api python -m bank_ops.cli train --version replica-v2
docker compose exec api python -m bank_ops.cli promote --version replica-v2 --actor equipo --reason "Ensayo réplica"
docker compose restart api
docker compose exec api python -m bank_ops.cli rollback --actor equipo --reason "Ensayo recuperación"
docker compose restart api
docker compose down
```

No usar down -v como limpieza habitual: elimina los modelos y registros. Los puertos solo se publican en localhost. Un worker y un operador; archivos locales no resistentes a manipulación. No utilizar con personas reales.

## Datos y decisiones

45 211 filas; manifiesto y checksum en data/provenance.json. Copia local normalizada, orden conservado. Excluir duration, age y day; edad solo para auditoría offline. No hay identificador de cliente ni fecha completa. El umbral 0.25 es didáctico y puede dar recall cero en validación: analizar el resultado sin ocultarlo.

## GitHub

Subir esta carpeta como raíz del repositorio para que se detecte .github/workflows. Cron semanal UTC y activación manual; no se accede a la computadora del estudiante. Artefactos de candidatos y de imagen conservados en Actions. Sin nube de pago obligatoria.
