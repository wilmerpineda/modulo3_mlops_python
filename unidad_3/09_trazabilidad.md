# Ciclo de vida y trazabilidad de artefactos

## Qué debe viajar con un modelo

El objeto serializado depende de transformaciones, versiones de librerías y columnas. Los metadatos del proyecto registran features, umbral, dataset, SHA-256 del modelo, versión de scikit-learn, Python, semilla, commit, fecha UTC y métricas de validación. `sin-repositorio` hace visible que aún no hay commit; no se fabrica uno.

```python
from bank_ops.model import read_model
estimator, metadata = read_model("baseline-v1")
print(metadata["data_sha256"])
print(metadata["features"])
print(metadata["validation"])
```

Guardar scaler y encoder dentro del Pipeline conserva el mismo procesamiento en entrenamiento e inferencia. El encoder admite niveles nuevos, pero eso no hace inocuo un cambio de categorías: se debe monitorear su frecuencia.

## Estados y responsabilidades
Propuesto, entrenado, evaluado, aprobado, activo y retirado son estados útiles. El ejemplo representa los archivos y el puntero, sin implementar un registro empresarial completo. Un registro dedicado como MLflow puede añadir búsqueda, permisos y metadatos centralizados; no elimina la necesidad de políticas.

La persona que entrena prepara evidencia; quien revisa cuestiona resultados y riesgos; el operador ejecuta la transición y confirma salud. En equipos pequeños pueden coincidir personas, pero deben quedar claras las acciones.

## Reproducibilidad y seguridad de artefactos
Una semilla no controla todas las diferencias de plataforma. Conservar lock, snapshot y configuración acerca la reproducción. SHA-256 detecta alteración respecto de una huella conocida, pero alguien con acceso a ambos archivos podría cambiar los dos. Los archivos joblib deben provenir de una fuente confiable, porque su carga puede ejecutar código.

**Ejercicio:** diseñe un inventario que permita responder qué datos, código y revisión produjeron la predicción con cierto identificador. Explique qué parte del inventario actual no resistiría manipulación y cómo la fortalecería.
