# Implementación con GitHub Actions

## Estructura del workflow

`on` define eventos; `jobs` agrupa trabajo; `steps` ejecuta comandos o acciones. El workflow `ci.yml` responde a PR, cambios en main y ejecución manual. Instala Python y Poetry, verifica el snapshot, ejecuta pytest, construye imagen y hace un smoke test HTTP.

```yaml
permissions:
  contents: read
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install poetry==2.1.3
      - run: poetry install --no-interaction
      - run: poetry run pytest -q
```

Este fragmento ilustra el núcleo; el archivo completo del proyecto añade build y evidencias. Las acciones se referencian por versión mayor para legibilidad docente; una política de mayor rigor fija commit SHA y automatiza actualizaciones revisadas.

## Calendario y artefactos
`retrain.yml` utiliza cron `17 5 * * 1`: lunes a las 05:17 UTC. Los workflows programados dependen de la rama predeterminada y pueden retrasarse; no son un temporizador de precisión. Existe también `workflow_dispatch` para demostración manual. [Comportamiento oficial](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows).

Un artefacto transporta resultados entre ejecuciones o hacia el revisor; una caché acelera dependencias y puede caducar. No tratar una caché como registro oficial del modelo. La retención debe corresponder al periodo de revisión y a la política de conservación.

## Seguridad y fallos
Permisos de lectura son suficientes para este proyecto. No hay credenciales cloud ni publicación a un registro externo. No introducir secretos en YAML o logs. Un PR no confiable no debe ejecutar código con secretos de producción.

La instalación sí requiere red para paquetes y contenedores en un runner nuevo; las pruebas no descargan datos. Esa distinción evita prometer ejecución completamente offline desde una máquina vacía.

**Práctica:** rompa intencionalmente una validación en una rama, observe el job fallido, repare el cambio y conserve ambos enlaces. No cree una captura de éxito sin ejecución real.
