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
