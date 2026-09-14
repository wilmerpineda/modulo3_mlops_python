# Ambiente y guía de estudio

## Cómo recorrer la edición ampliada

El libro está organizado como un manual técnico avanzado. Cada capítulo comienza con una síntesis y continúa con una profundización que formaliza el problema, conecta el concepto con Bank Marketing y termina con preguntas o casos. No es necesario ejecutar código en la primera lectura: identifique primero qué se mide, qué conclusión permite y qué evidencia falta.

Un recorrido recomendado combina tres capas: leer los capítulos de la unidad, ejecutar el notebook relacionado y aplicar después el concepto al proyecto inicial. Las cajas desplegables contienen orientación formativa y se consultan después de escribir una respuesta propia. Las prácticas opcionales no aumentan los entregables de la actividad.

| Unidad | Notebook o práctica | Producto de comprensión |
|---|---|---|
| 1. Monitoreo | 01–04 | Diagnóstico que separa señal, impacto y evidencia ausente |
| 2. Observabilidad | 03 y Compose | Consulta con unidad, ventana, población y runbook |
| 3. Actualización | 06 | Decisión de candidato y protocolo de recuperación |
| 4. CI/CD | Proyecto inicial en su propio repositorio | Ejecución que muestra qué control permitió o bloqueó avanzar |
| 5. Testing y gobernanza | 05 y pytest | Propiedad probada, denominadores, riesgos y responsables |
| 6. Escalabilidad | 06 y prueba de carga | Recomendación de capacidad con supuestos y costos |

Mantenga un cuaderno de evidencias con fecha UTC, versión, ventana o dataset, comando, resultado y explicación. Una captura aislada no sustituye esos datos. En los ejemplos se distinguen resultados históricos, simulaciones e hipótesis de costo; conserve esa distinción en sus conclusiones.

## Instalación reproducible

Abra una terminal en `actividad_3/proyecto_inicial`. Instale Python 3.11 y Poetry 2.1.3. El material usa versiones fijadas para evitar cambios de API entre ejecuciones; no supone que sean las versiones más recientes.

```powershell
poetry env use 3.11
poetry install
poetry run python -m bank_ops.data
poetry run python -m bank_ops.cli train --version baseline-v1
poetry run python -m bank_ops.cli promote --version baseline-v1 --actor equipo --reason "Inicio del laboratorio"
poetry run uvicorn bank_ops.api:app --host 127.0.0.1 --port 8000
```

Mantenga la API en una terminal y use otra para los clientes. Las versiones son inmutables: si `baseline-v1` existe, reutilícela o elija un nombre nuevo; no sobrescriba un resultado para ocultar diferencias.

```powershell
Invoke-RestMethod http://127.0.0.1:8000/ready
poetry run pytest -q
poetry run python -m bank_ops.cli monitor --version baseline-v1
```

El proyecto inicial contiene tareas explícitas en `TAREAS.md`; sus pruebas de ampliación permanecen pendientes hasta completarlas. El baseline y la API funcionan desde el inicio.

## Contenedores

Detenga la API anterior si ocupa el puerto 8000. Inicie Docker Desktop y espere a que `docker info` responda.

```powershell
docker compose up --build -d
docker compose ps
docker compose logs api
```

Abra API en `http://localhost:8000/docs`, Prometheus en `http://localhost:9090` y Grafana en `http://localhost:3000`. El dashboard permite lectura anónima solo para este laboratorio, con puertos publicados en loopback. No copiar esa configuración sin revisión a un servidor público.

Los modelos del contenedor viven en un volumen distinto de los artefactos de Python local. Un cambio local no cambia el contenedor. Use `docker compose exec api python -m bank_ops.cli ...` para operar el registro del contenedor y `docker compose restart api` después de una promoción.

## Notebook y libro

Instale el kernel en el entorno que use Jupyter o seleccione directamente el intérprete Poetry. Los notebooks encuentran la raíz del material sin rutas personales. Ejecútelos del 01 al 06. El proyecto del estudiante acompaña el libro; no mueva los notebooks sin llevar sus datos y código.

Para reconstruir el HTML desde la raíz del módulo:

```powershell
python -m pip install -r requirements-book.txt
jupyter-book build . --all
python -m http.server 8080 --directory _build/html
```

Abra `http://localhost:8080`. La compilación usa las salidas ya verificadas de los notebooks; el script tools/validar_notebooks.py vuelve a ejecutarlos por separado. Esto evita que una visita o compilación vuelva a entrenar modelos.

## Diagnóstico rápido

| Síntoma | Comprobación y acción |
|---|---|
| 503 en `/ready` | Verificar `current.json`, artefacto y checksum; entrenar/promover si faltan |
| 422 en `/predict` | Revisar tipos, campos extra y rangos en `/docs` |
| Grafana sin curvas | Generar tráfico, esperar dos scrapes y revisar target Prometheus |
| Puerto ocupado | Detener la otra API o ajustar el puerto publicado |
| No hay motor Docker | Iniciar Docker Desktop; no confundir CLI instalada con daemon activo |
| Versión ya existe | Usar otra versión; conservar evidencia previa |
| Falla checksum | Comparar procedencia; no recalcular la huella para aceptar silenciosamente datos alterados |

## Qué significa completar el módulo

La meta no es memorizar nombres de herramientas. Al finalizar, el estudiante debe poder reconstruir una afirmación operativa: qué versión produjo un resultado, sobre qué población se midió, cuál fue el límite de la evidencia, qué control autorizó una transición y cómo se verificó la recuperación. Si una conclusión depende de etiquetas todavía ausentes o de una infraestructura que no pudo ejecutarse, se comunica como pendiente y se propone una comprobación concreta.
