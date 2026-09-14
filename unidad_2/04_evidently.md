# Evidently: del DataFrame al informe

## Preparar el reporte

Evidently compara datasets y genera evidencia exportable. Se fija la versión usada en el proyecto: ejemplos de APIs antiguas no deben mezclarse con la interfaz `Dataset`, `DataDefinition` y `Report` utilizada aquí.

```python
from evidently import Dataset, DataDefinition, Report
from evidently.presets import DataDriftPreset
from bank_ops.config import NUMERIC, CATEGORICAL, FEATURES

definition = DataDefinition(numerical_columns=NUMERIC,
                            categorical_columns=CATEGORICAL)
reference = Dataset.from_pandas(stable[FEATURES], data_definition=definition)
current = Dataset.from_pandas(shifted[FEATURES], data_definition=definition)
snapshot = Report([DataDriftPreset()]).run(
    reference_data=reference, current_data=current)
snapshot.save_html("drift.html")
snapshot.save_json("drift.json")
```

El HTML permite explorar las distribuciones y resultados; JSON facilita conservación y procesamiento. Revisar el método y umbral que el reporte asigna a cada columna: las selecciones predeterminadas pueden depender de tipo y tamaño. Para una política estable hay que fijar y documentar la configuración, no depender silenciosamente de cambios de versión.

## Lectura del informe
Comenzar por tamaños de las ventanas y calidad de columnas; luego inspeccionar qué variables cambiaron y en qué dirección. Vincular el cambio con el contexto: una columna `contact` dominada por `unknown` podría ser una modificación del canal o una falla del extractor. El reporte identifica la diferencia; la causa necesita investigación.

El proyecto crea informes `drift_stable`, `drift_shift` y `drift_degraded`. En el último, las entradas son idénticas al control estable y se modifican etiquetas fuera de las columnas analizadas. Su utilidad es demostrar una limitación: detectar drift en X no basta para monitorear calidad predictiva.

## Integración por lotes
Ejecutar el reporte después de validar el lote y antes de decidir su uso. Guardar ventana, modelo, referencia, versión de herramienta y resultados. No generar un reporte completo en cada llamada HTTP: aumenta latencia y mezcla observabilidad con inferencia. En este laboratorio el comando `monitor` trabaja fuera de la API.

**Práctica:** abra los tres HTML, seleccione una variable numérica y una categórica, compare distribuciones y escriba una hipótesis contrastable. Cite el reporte concreto, no solo una captura.

**Consulta:** [interfaz de la biblioteca](https://docs.evidentlyai.com/docs/library/overview) y [preset de drift](https://docs.evidentlyai.com/metrics/preset_data_drift).

## Captura del reporte ejecutado

![Reporte real de Evidently con cambios detectados en balance y contact](../images/evidently_real.png)

Fuente: captura de la ejecución del laboratorio. Se detectan cambios en 2 de 13 columnas (15.4 %). El encabezado global indica que no se supera su regla agregada de 50 %. No hay contradicción: la señal por columna y la decisión agregada son distintas. Una variable importante puede requerir investigación aunque el indicador global no se active. No ajustar el umbral solamente para obtener un aviso rojo.
