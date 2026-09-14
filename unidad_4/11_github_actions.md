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

<!-- MANUAL AVANZADO -->

## Dos workflows distintos dentro del material

```{important}
En el repositorio del libro, `.github/workflows/book.yml` compila y publica documentación. Los archivos de ML están dentro de `actividad_3/proyecto_inicial/.github/workflows/`; GitHub no los ejecuta desde esa carpeta anidada. Al crear el repositorio de la actividad, el equipo debe usar el contenido de proyecto_inicial como raíz. Su CI contiene `compileall` deliberadamente y A3-03 exige sustituir esa comprobación por las pruebas. No confundir el éxito de GitHub Pages con la finalización del laboratorio de ML.
```

El workflow de publicación instala dependencias del libro, compila con advertencias tratadas como errores y entrega HTML a GitHub Pages. En pull requests comprueba la compilación; el despliegue se limita a main. Las salidas guardadas de notebooks se renderizan, pero esa compilación no vuelve a ejecutarlos. La ejecución de notebooks se valida por separado para evitar que cada cambio editorial entrene de nuevo.

El workflow `ci.yml` del starter instala el entorno del proyecto, verifica el snapshot, compila fuentes como tarea inicial, construye una imagen y consulta readiness. El workflow `retrain.yml` entrena dos versiones y llama a compare, que exige completar A3-01. Esa lectura del estado real evita prometer que el proyecto entregado ya satisface todas las tareas evaluadas.

## Leer YAML como un programa con contexto

`on` define qué eventos pueden iniciar una ejecución. `jobs` define unidades de ejecución y sus dependencias; cada job puede tener un runner y entorno diferentes. `steps` ejecuta acciones o comandos en orden dentro del job. Los archivos creados por un paso suelen estar disponibles para los siguientes del mismo job, pero no pasan mágicamente a otro runner. Para transferirlos se usa un artefacto u otro almacenamiento explícito.

`uses` referencia una acción reutilizable; `run` ejecuta comandos en el shell configurado. La versión de una acción y la versión de Python cumplen funciones distintas. Actualizar `setup-python` no actualiza automáticamente el `python-version` declarado ni las bibliotecas fijadas en Poetry. Los ejemplos de ML mantienen las versiones mayores de acciones con las que se preparó el proyecto; el workflow del libro puede usar otras sin que ello implique incompatibilidad de los paquetes de ML.

El directorio de trabajo es otra dependencia. Los comandos `poetry install` y `docker build .` esperan encontrar sus archivos en la raíz del proyecto de actividad. Si se copian al workflow raíz del libro sin ajustar la ruta, fallarán o construirán otro contexto. La opción pedagógica elegida es un repositorio separado para la actividad, manteniendo claros ambos productos. [Sintaxis oficial de workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax).

## Revisar cada etapa del CI de ML

Checkout obtiene la revisión que se verificará. Setup Python fija el intérprete. La instalación de Poetry prepara la herramienta que interpreta el lock; `poetry install` instala dependencias y el paquete local. La validación del snapshot protege identidad y contrato antes de gastar tiempo en build. Las pruebas, una vez incorporadas por el equipo, verifican comportamiento que la compilación sintáctica no observa.

El build produce `bank-ops:ci` dentro del runner. El contenedor se inicia y se consulta readiness con espera acotada. Un bucle de espera no demuestra éxito por terminar: la consulta final con fallo explícito confirma el estado. Si nunca hubo readiness, la ejecución debe permanecer fallida. Los logs del contenedor ayudan a distinguir error de importación, artefacto ausente, puerto y carga del modelo.

En un push a main se guarda la imagen en un archivo comprimido y se carga como artefacto. En un PR puede verificarse el build sin conservar esa entrega final. La separación permite revisar contribuciones sin crear un entregable de liberación para cada intento. El comando de logs condicionado con `always()` intenta capturar diagnóstico incluso después de fallos anteriores.

## Variables, permisos y secretos

Las variables de entorno declaran configuración como desactivar telemetría de la biblioteca en el laboratorio. No toda variable es un secreto. Los secretos son credenciales o valores que requieren protección y no deben incorporarse a archivos versionados. Imprimir el entorno completo para diagnosticar un error puede exponer información innecesaria; conviene consultar solo las variables relevantes y no sensibles.

El permiso `contents: read` es suficiente para obtener el código en los flujos de ML actuales. Publicar GitHub Pages necesita permisos de despliegue específicos, asignados al job correspondiente del libro. No se debe copiar esa capacidad a todos los jobs por comodidad. La autorización debe seguir la acción concreta y el origen del código que se ejecuta.

Un runner alojado comienza con un entorno preparado por el proveedor, pero el workflow todavía depende de red para instalar paquetes e imágenes. Las pruebas usan el snapshot incluido y no descargan datos de UCI. Esta diferencia permite que un fallo de internet al instalar no se describa incorrectamente como fallo de calidad del dataset.

## Calendario, concurrencia y nombres de ejecución

El cron `17 5 * * 1` expresa lunes a las 05:17 UTC; en Bogotá corresponde a las 00:17 para ese desfase horario. El programador no garantiza ejecución exacta al segundo y trabaja sobre la rama predeterminada. La ejecución manual permite ensayar el flujo sin esperar al calendario. Si el proyecto es un fork o hay políticas del repositorio que deshabilitan acciones, revisar esa configuración antes de concluir que el cron está mal. [Eventos y schedule](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows).

El grupo de concurrencia de retraining evita solapar ejecuciones activas de ese grupo según el comportamiento de la plataforma. No es una cola durable de todos los eventos ni coordina procesos ejecutados fuera de GitHub. El candidato y baseline se crean con nombres fijos dentro de un runner limpio; el artefacto de salida incorpora el identificador de ejecución. Si esos comandos se repiten en un registro local persistente, la inmutabilidad rechazará nombres existentes.

Las condiciones `if` deciden si un paso o job debe ejecutarse; los filtros de eventos deciden si la ejecución existe. Confundirlos puede producir un workflow que se inicia pero omite la etapa esperada. La interfaz de Actions muestra pasos omitidos y fallidos; leer ambos estados ayuda a interpretar un resultado global sin reducirlo a una captura verde.

## Conservar evidencia útil

Un artefacto de comparación debería incluir versiones, métricas, política y resultado, no solo la palabra «aprobado». Los logs muestran recorrido y errores; el JSON conserva valores estructurados para revisión. La retención limitada exige descargar o archivar lo necesario antes de que expire si la evaluación del curso ocurre después. [Artefactos de workflow](https://docs.github.com/en/actions/tutorials/store-and-share-data).

En el starter, si compare lanza una excepción por A3-01 pendiente, la redirección puede dejar un archivo vacío o parcial y el paso falla. La subida posterior, sin condición especial, no debe asumirse ejecutada. Después de completar la tarea se revisará el contenido real del JSON. Para un pipeline industrial convendría generar archivos de salida de forma controlada y guardar diagnósticos aun cuando la comparación no pueda completarse.

Una captura debe mostrar contexto suficiente: nombre del workflow, revisión, fecha y paso relevante. El enlace a la ejecución permite inspeccionar detalles; la captura sola puede ocultar que las pruebas fueron omitidas. El informe del equipo vincula fallo deliberado y reparación, explicando qué invariante protegió el check.

## Práctica guiada de lectura y fallo

Primero identifique en el YAML del starter el paso que todavía no ejecuta pytest. Después diseñe un cambio que deba fallar una prueba existente de contrato, sin alterar permanentemente los datos originales. Ejecútelo en una rama del repositorio de actividad, revise el log y repare el cambio. La práctica no exige publicar datos privados ni usar un registro cloud.

```{admonition} Comprobación conceptual
:class: dropdown
Si el workflow del libro pasa y el de retraining falla por NotImplementedError, ¿hay contradicción? No: verifican productos distintos y el segundo depende de una tarea pendiente. Si el CI de ML pasa usando compileall, tampoco demuestra que las pruebas de recuperación estén implementadas. La conclusión debe nombrar el workflow y la propiedad efectivamente comprobada.
```

El objetivo es poder explicar una ejecución paso por paso: qué revisión obtuvo, qué instaló, qué validó, qué produjo y dónde quedó la evidencia. Esa explicación es más importante que memorizar la sintaxis de una acción concreta.
