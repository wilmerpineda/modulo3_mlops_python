# Jenkins y GitLab CI: equivalencias y decisiones

## Un mismo contrato operativo

El proveedor cambia, pero se conserva la secuencia: obtener fuente, instalar dependencias fijadas, validar datos, probar, construir y conservar artefactos. Los comandos del paquete permiten esa portabilidad. No duplicar la lógica del modelo dentro del YAML de cada plataforma.

### Jenkins declarativo

```groovy
pipeline {
  agent any
  stages {
    stage('Instalar') { steps { sh 'poetry install --no-interaction' } }
    stage('Datos y pruebas') { steps {
      sh 'poetry run python -m bank_ops.data'
      sh 'poetry run pytest -q'
    } }
    stage('Imagen') { steps { sh 'docker build -t bank-ops:ci .' } }
  }
}
```

Este ejemplo presupone un agente Linux con Python, Poetry y acceso a Docker. Administrar agentes, actualizaciones y permisos forma parte del costo operativo de Jenkins. `sh` no sirve directamente en un agente Windows; allí se usaría `bat` o PowerShell con comandos equivalentes.

### GitLab CI

```yaml
image: python:3.11.12-slim
stages: [verify]
verify:
  stage: verify
  before_script:
    - pip install poetry==2.1.3
    - poetry install --no-interaction
  script:
    - poetry run python -m bank_ops.data
    - poetry run pytest -q
```

El build de imágenes requiere un runner y mecanismo de construcción adecuados. No asumir Docker disponible porque el job use una imagen Python. La configuración de runners, registros y secretos queda fuera de la actividad obligatoria.

| Decisión | GitHub Actions | Jenkins | GitLab CI |
|---|---|---|---|
| Definición | YAML en `.github/workflows` | Jenkinsfile | `.gitlab-ci.yml` |
| Ejecución | Runner | Agente | Runner |
| Integración | GitHub | Plugins y servicios | GitLab |
| Mantenimiento | Depende del runner | Servidor y agentes propios | Depende de modalidad |

**Ejercicio:** documente qué infraestructura adicional necesitaría para trasladar el CI docente a una red institucional cerrada. La respuesta debe incluir acceso a paquetes, imágenes, almacenamiento y responsables.

<!-- MANUAL AVANZADO -->

## Portabilidad del procedimiento frente a portabilidad del YAML

La lógica de datos, entrenamiento y evaluación vive en el paquete Python y su CLI. Esa elección permite cambiar de orquestador sin reescribir la política estadística en otro lenguaje. Lo portable son los comandos y sus contratos, no necesariamente las condiciones, permisos o almacenamiento de cada plataforma. Copiar palabras clave entre YAML distintos puede producir una configuración válida con un comportamiento diferente.

Para trasladar el proyecto se deben conservar revisión de código, lock, snapshot, directorio de trabajo y criterios de éxito. También hay que definir cómo obtiene el ejecutor sus dependencias y cómo conserva resultados. Un agente que ya tiene bibliotecas instaladas puede ocultar una dependencia no declarada. Una reproducción sobre un ejecutor limpio detecta esas diferencias y evita que la plataforma parezca resolver mágicamente el entorno.

Los fragmentos de este capítulo son ejemplos de configuración para estudiar equivalencias. No se afirma que hayan sido ejecutados en servidores Jenkins o GitLab del curso. GitHub Actions sigue siendo la plataforma de la actividad; desplegar y administrar las alternativas no añade requisitos obligatorios.

## Jenkins: responsabilidades de servidor y agente

El controlador organiza trabajos y los agentes ejecutan comandos. La elección del agente determina sistema operativo, herramientas, red y acceso a Docker. `agent any` significa que se acepta un agente disponible conforme a la configuración, no que todos los agentes tengan las dependencias correctas. En una instalación heterogénea convendría una etiqueta que identifique explícitamente el entorno apto.

El pipeline declarativo agrupa `stages` y `steps`, permite límites de tiempo y acciones posteriores. Un bloque `post` puede conservar diagnóstico cuando una etapa falla. Para evitar mezclar salidas entre builds, los espacios de trabajo y nombres de artefactos deben tener una política clara. El servidor no debe convertirse en un directorio compartido donde la última ejecución decide silenciosamente qué modelo existe. [Referencia de Pipeline de Jenkins](https://www.jenkins.io/doc/book/pipeline/syntax/).

```groovy
// Ejemplo conceptual para un agente Linux preparado por la institución.
pipeline {
  agent { label 'python311-docker' }
  options {
    timeout(time: 20, unit: 'MINUTES')
    disableConcurrentBuilds()
  }
  stages {
    stage('Entorno') {
      steps { sh 'poetry install --no-interaction' }
    }
    stage('Contrato') {
      steps { sh 'poetry run python -m bank_ops.data' }
    }
    stage('Pruebas') {
      steps { sh 'poetry run pytest -q --junitxml=pytest-results.xml' }
    }
  }
  post {
    always {
      archiveArtifacts artifacts: 'pytest-results.xml', allowEmptyArchive: true
    }
  }
}
```

La etiqueta presupone que el administrador definió ese agente; no se crea por escribir su nombre. El timeout limita una ejecución, pero debe complementarse con limpieza de procesos o contenedores cuando corresponda. `allowEmptyArchive` permite intentar conservar evidencia aunque la instalación haya fallado antes de producir XML; no hace que las pruebas fallidas pasen. La distinción entre diagnóstico tolerante y verificación estricta debe mantenerse.

En Windows se usarían pasos de PowerShell o `bat`, con rutas y activación de entorno compatibles. Cambiar `sh` por otro comando sin revisar redirecciones, variables y códigos de salida puede modificar el significado del pipeline. La CLI de Python reduce esa superficie, pero no elimina diferencias del shell.

## GitLab CI: jobs, stages y artefactos

Una etapa agrupa jobs con un orden general; las dependencias pueden refinarse para expresar un grafo. Cada job recibe un entorno definido por el runner y su ejecutor. La declaración `image` se interpreta según ese ejecutor: una imagen Python en un job de contenedor no implica que exista un daemon Docker accesible para construir otras imágenes. [Referencia YAML de GitLab CI](https://docs.gitlab.com/ci/yaml/).

```yaml
# Ejemplo para un repositorio cuya raíz es proyecto_inicial.
image: python:3.11-slim
stages: [verify]
verify:
  stage: verify
  before_script:
    - python -m pip install poetry==2.1.3
    - poetry install --no-interaction
  script:
    - poetry run python -m bank_ops.data
    - poetry run pytest -q --junitxml=pytest-results.xml
  artifacts:
    when: always
    paths:
      - pytest-results.xml
    expire_in: 14 days
```

La imagen de este fragmento es ilustrativa y mutable; para una reproducción institucional se fijaría un digest validado, como se hace con la imagen de servicio del proyecto. El artefacto se intenta conservar incluso si las pruebas fallan, pero puede no existir si falló la instalación. Ese caso debe leerse en los logs y no confundirse con una suite que ejecutó cero pruebas por éxito.

Separar build de verificación permitiría reservar un runner con capacidades de construcción solo cuando pasan los checks. Montar un socket de Docker o habilitar ejecución privilegiada tiene implicaciones de acceso al host; no debe hacerse como paso automático para resolver un error de permisos sin revisar el entorno. La actividad no requiere configurar esa infraestructura.

## Comparar equivalencias de manera verificable

| Necesidad | GitHub Actions | Jenkins | GitLab CI |
|---|---|---|---|
| Fuente del pipeline | Workflow versionado | Jenkinsfile en SCM | Archivo CI versionado |
| Capacidad de ejecución | Runner y etiquetas | Agente y etiquetas | Runner, tags y ejecutor |
| Secuencia | Jobs, needs y steps | Stages y steps | Stages, jobs y needs |
| Diagnóstico posterior | Condiciones como always | Bloques post | Política de artefactos y after_script |
| Resultado transportable | Artefactos de ejecución | Archivado de artefactos | Artefactos de job |
| Control de liberación | Entornos y permisos | Etapas y controles configurados | Entornos y reglas configuradas |

La tabla describe funciones comparables, no garantías idénticas. Por ejemplo, una aprobación puede depender de características disponibles, configuración y permisos de la instalación. Antes de migrar se verifica quién puede cambiar el pipeline, quién puede aprobar, qué código accede a credenciales y cuánto tiempo se conserva la evidencia. La equivalencia se demuestra ejecutando escenarios, no solo traduciéndoles el nombre.

## Red institucional y dependencias externas

En una red cerrada deben existir fuentes permitidas para paquetes Python e imágenes base, resolución de nombres y certificados correctos. Un proxy puede permitir navegación desde el escritorio y bloquear al servicio que ejecuta el agente. La cuenta de servicio, la configuración del daemon y la del shell pueden tener accesos diferentes. El diagnóstico debe identificar cuál proceso intentó la conexión y a qué recurso.

El snapshot incluido permite que los tests no dependan de descargar UCI en cada ejecución. Las dependencias siguen necesitando una fuente en la primera instalación. Una caché local reduce tráfico, pero no reemplaza un repositorio de paquetes administrado si se requiere disponibilidad prolongada. Para imágenes, se debe conservar la identidad por digest y documentar cómo se actualiza sin romper la reproducción.

Los certificados no deberían desactivarse globalmente para que una instalación funcione. La solución adecuada revisa cadena de confianza, proxy y configuración autorizada. El libro no proporciona comandos que omitan validación TLS; el objetivo es comprender por qué acceso desde el navegador y acceso desde un runner son hechos distintos.

## Costo total y mantenimiento

Comparar plataformas solo por minutos de ejecución omite administración, actualizaciones, disponibilidad de agentes, almacenamiento y respuesta a incidentes. Jenkins puede adaptarse a una infraestructura existente y requiere responsables de servidor y plugins. Los runners propios en otras plataformas también requieren mantenimiento; «alojado en GitHub» o «GitLab» no describe por sí solo quién administra la máquina que ejecuta el job.

Una matriz de decisión debe incluir integración con identidad institucional, acceso a datos, habilidades del equipo, retención de evidencias y capacidad de aislar contribuciones no confiables. Para el curso se elige GitHub Actions porque el repositorio y la publicación ya viven allí y el laboratorio cabe en su flujo. Esa elección pedagógica no pretende demostrar que sea superior para todas las organizaciones.

## Ensayo de migración sin infraestructura nueva

Describa cómo trasladaría un flujo con validación de snapshot, pytest y build. Identifique qué comandos conservaría literalmente y qué configuración cambiaría. Después analice tres fallos: instalación sin red, tests fallidos y artefacto ausente. Para cada plataforma, indique dónde esperaría el diagnóstico y qué etapa debe quedar bloqueada. No es necesario desplegar servidores para razonar sobre esas dependencias.

```{admonition} Criterio de una respuesta sólida
:class: dropdown
La respuesta conserva el contrato del paquete y diferencia entorno de ejecución, secuencia y transporte de resultados. No da por hecho Docker dentro de una imagen Python, ni interpreta un archivo de configuración como evidencia de una ejecución real. Incluye responsables de infraestructura y un mecanismo para identificar la revisión verificada.
```

La portabilidad valiosa permite cambiar de plataforma manteniendo las mismas preguntas de calidad: qué se probó, qué falló, qué artefacto se entregó y qué decisión autorizó usarlo. El YAML es una representación de ese procedimiento, no su justificación.
