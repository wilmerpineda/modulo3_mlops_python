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

<!-- MANUAL AVANZADO -->

## De un archivo de modelo a una cadena de evidencia

Un archivo serializado responde qué objeto se guardó; no explica por qué se produjo, con qué datos se entrenó ni quién decidió usarlo. La trazabilidad conecta decisiones y artefactos: snapshot, transformación, configuración, ejecución, evaluación, aprobación, despliegue y predicción. No todos esos vínculos existen con el mismo nivel de garantía en el laboratorio, y esa diferencia debe ser visible.

El proyecto incluye metadatos junto al `model.joblib`. La API devuelve versión y un identificador por predicción, y el log conserva score, umbral y hora. A partir de la versión puede buscarse el manifiesto del modelo; desde él, el hash de datos y el commit. Esto permite reconstruir una parte importante del recorrido sin almacenar todos los atributos del solicitante en el log del servicio.

No obstante, un commit no garantiza que el directorio estuviera limpio cuando se entrenó. Si se modificó código sin confirmarlo, `git rev-parse HEAD` identifica el último commit, no esas modificaciones. Tampoco una semilla garantiza identidad binaria entre plataformas. Una ficha rigurosa debe declarar esas fronteras y, en una ampliación industrial, registrar configuración efectiva y estado de trabajo o entrenar desde una revisión inmutable verificada.

## Identificadores y hashes cumplen funciones distintas

Un nombre como `candidate-v2` es una etiqueta humana y local. Un hash identifica contenido con alta sensibilidad a cambios de bytes. Un identificador de ejecución permite distinguir intentos, incluso cuando producen el mismo contenido. La versión de un contrato expresa compatibilidad. Usar un único campo «versión» para todas estas funciones dificulta responder preguntas concretas.

Considere dos ejecuciones con la misma semilla y datos. Pueden generar estimadores equivalentes y archivos con diferencias de serialización o metadatos. Un hash distinto no prueba una diferencia predictiva relevante; un hash igual sí confirma identidad de bytes respecto de la referencia usada. Para evaluar comportamiento se necesitan entradas de prueba y resultados, además de integridad.

La huella del CSV requiere preservar bytes al moverlo entre sistemas. Git puede normalizar finales de línea de archivos de texto; el repositorio declara `*.csv -text` para evitar modificar el snapshot al clonar en Linux o Windows. Esa decisión protege el contrato del dataset y explica por qué un cambio de separador o codificación, aunque conserve valores, debe documentarse como otra representación del archivo.

```python
# Ejemplo autónomo de sensibilidad de contenido, sin alterar el dataset.
import hashlib
a = b"x,y\n1,0\n"
b = b"x,y\r\n1,0\r\n"
print(hashlib.sha256(a).hexdigest())
print(hashlib.sha256(b).hexdigest())
assert hashlib.sha256(a).digest() != hashlib.sha256(b).digest()
```

El ejemplo muestra por qué una discrepancia de hash inicia una investigación y no demuestra por sí misma intención maliciosa o corrupción semántica. Recalcular automáticamente la huella esperada para aceptar el archivo haría inútil el control. Se debe identificar la causa y, si la transformación es legítima, aprobar una nueva referencia con procedencia.

## Manifiesto mínimo y ampliaciones

| Campo conceptual | Pregunta de auditoría | Estado en el proyecto |
|---|---|---|
| Datos y partición | ¿Qué ejemplos sustentaron el ajuste? | Hash, filas y política 60/20/20 |
| Código | ¿Qué revisión contiene la implementación? | Commit o ausencia explícita |
| Entorno | ¿Qué bibliotecas interpretan el objeto? | Python, sklearn y lock del proyecto |
| Features y umbral | ¿Qué contrato y política se sirvieron? | Metadatos verificables |
| Evaluación | ¿Con qué evidencia se comparó? | Métricas de validación y reportes |
| Acción | ¿Quién declaró promover o revertir? | Actor, motivo y hora en log local |
| Predicción | ¿Qué versión produjo esta respuesta? | Identificador y versión HTTP |
| Aprobación autenticada | ¿Quién estaba autorizado? | No implementada por el registro local |

El manifiesto debe describir hechos reproducibles y separar afirmaciones de aprobación. Un campo `educational_only` comunica propósito, pero no impide técnicamente otros usos. Una lista de features permite comprobar compatibilidad, pero no describe por completo su semántica, unidades o proceso de captura. Esa información pertenece también a documentación de datos y contrato.

Una model card resume usos previstos, límites, evaluación y consideraciones por grupos. Una ficha del dataset describe origen, composición y condiciones de recolección. Son artefactos complementarios: el primero no reemplaza la documentación de procedencia y el segundo no explica por sí solo el comportamiento de un estimador. [Model Cards](https://arxiv.org/abs/1810.03993) y [Datasheets for Datasets](https://arxiv.org/abs/1803.09010) ofrecen marcos primarios para esas preguntas.

## Reproducibilidad en tres niveles

La reproducción de datos verifica que se usa el mismo snapshot y las mismas particiones. La reproducción del procedimiento verifica código, configuración y entorno. La reproducción del resultado compara artefactos o métricas con tolerancias apropiadas. Es posible lograr la primera y fallar en la segunda por una dependencia nueva; también lograr procedimiento equivalente y obtener pequeñas diferencias numéricas por plataforma.

Por eso el informe no debería afirmar simplemente «reproducible» sin explicar qué se verificó. En el laboratorio se fijan dependencias, semilla y datos, y se ejecutan notebooks y pruebas. Las métricas se interpretan con tolerancias; no se exige que el tiempo de entrenamiento sea idéntico ni que un archivo joblib sea portable entre cualquier versión futura. [Persistencia de modelos en scikit-learn](https://scikit-learn.org/1.6/model_persistence.html).

Una reproducción independiente debe comenzar en un entorno limpio y seguir instrucciones documentadas. Si requiere un archivo no versionado que solo existe en el computador del autor, la cadena está incompleta. La descarga del proyecto incluye datos y manifiesto; los reportes generados se reconstruyen o se conservan como evidencias separadas, según el objetivo de la revisión.

## Integridad no equivale a autenticidad

SHA-256 permite comparar contenido con una huella confiable. Si un atacante o un operador con permisos cambia modelo y manifiesto juntos, el control local puede aprobar ambos. Para mayor garantía se requiere proteger quién publica la referencia, conservar auditoría en otro dominio de acceso y, cuando corresponda, firmar artefactos y verificar su procedencia. La complejidad debe responder al riesgo, no a una lista de herramientas.

Los formatos basados en pickle, incluido joblib en este uso, pueden ejecutar código al cargar objetos. Verificar la huella contra un manifiesto entregado por la misma fuente desconocida no vuelve segura esa fuente. El laboratorio carga artefactos propios; no solicita descargar modelos serializados de terceros. La frontera de confianza incluye al productor del archivo y al mecanismo que distribuye su identidad.

El log local tampoco es inviolable. Puede truncarse, editarse o perderse con el volumen. Es suficiente para enseñar vínculos y revisar acciones de un operador, pero un sistema con responsabilidades formales necesitaría almacenamiento con controles de acceso, retención y auditoría independientes. La afirmación correcta describe qué alteraciones se detectan y cuáles permanecen posibles.

## Retención, privacidad y costo

Retener todas las entradas facilita ciertos análisis, pero aumenta exposición y costo. El proyecto conserva identificadores y salidas en el log de API, mientras que los análisis por edad se hacen sobre lotes separados. Esta minimización limita qué diagnósticos pueden reconstruirse desde el log aislado. El diseño debe aceptar ese intercambio explícitamente, no prometer análisis que los campos guardados no permiten.

La retención de modelos debe cubrir el periodo de recuperación previsto y los vínculos de auditoría necesarios. Borrar un modelo anterior porque «ya no está activo» puede impedir rollback; conservar indefinidamente todo también tiene costos. Una política define plazos, responsables y excepciones por incidentes. La limpieza de volúmenes de Docker no sustituye esa política.

```{admonition} Ejercicio de auditoría
:class: dropdown
Parta de un prediction_id y enumere los saltos necesarios hasta llegar al snapshot. Marque cuáles son búsquedas implementadas y cuáles requieren información adicional. Después suponga que el entrenamiento se hizo con cambios sin commit: explique qué vínculo se rompe y qué evidencia habría que añadir. No basta con mostrar una lista de hashes sin explicar qué conectan.
```

La trazabilidad útil reduce el tiempo para responder preguntas concretas durante un incidente. Su calidad se evalúa intentando reconstruir una predicción y una decisión de promoción, no contando campos en un JSON.
