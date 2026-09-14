# Módulo 3 · MLOps en Python

**[Leer el Jupyter Book](https://wilmerpineda.github.io/modulo3_mlops_python/)**

Operaciones, monitoreo y automatización continua: 18 capítulos, seis notebooks con resultados, diagramas Mermaid e imágenes, actividad integradora y proyecto inicial con Bank Marketing.

## Contenido
- Monitoreo, data drift, concept drift y desempeño con etiquetas tardías.
- Evidently, Prometheus y Grafana.
- Retraining, comparación de candidatos, promoción y rollback.
- CI/CD, GitHub Actions y ejemplos de Jenkins/GitLab CI.
- Testing, gobernanza, equidad, resiliencia y costos.

## Construir el libro
Con Python 3.11, desde un entorno virtual:
```bash
python -m pip install -r requirements-book.txt
jupyter-book build . --all
python -m http.server 8080 --bind 127.0.0.1 --directory _build/html
```
Abrir http://localhost:8080. La compilación utiliza las salidas guardadas de los notebooks. Para ejecutarlos, instalar las dependencias siguiendo [la guía de estudio](guia_estudio.md) y luego ejecutar `python tools/validar_notebooks.py`.

## Actividad
Consultar [la actividad 3](actividad_3.md) y [el proyecto inicial](actividad_3/proyecto_inicial/README.md). La descarga ZIP está incorporada en el libro. Algunas tareas y una prueba omitida son deliberadas y se explican en TAREAS.md.

## Publicación
Cada push a main compila el libro y lo publica con GitHub Actions en GitHub Pages. Los pull requests solo comprueban la compilación. El HTML generado no se versiona.

Los documentos Word institucionales se distribuyen como material complementario por el docente. La solución docente no forma parte de este repositorio.

## Alcance de las evidencias
Los seis notebooks se ejecutaron antes de publicar. Los datos proceden de una copia local de Bank Marketing; consultar data/provenance.json del proyecto. Los escenarios son educativos. La imagen Docker de la API se construyó; la comprobación integrada de Prometheus/Grafana quedó pendiente por un error de almacenamiento local. El workflow de este repositorio publica el libro; los workflows de ML del proyecto inicial deben completarse y ejecutarse como parte de la actividad.
