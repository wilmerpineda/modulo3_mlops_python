# Código del proyecto y mapa de componentes

El código siguiente corresponde al proyecto inicial distribuido. Las tareas del gate y las pruebas de actualización son deliberadas y están señaladas en TAREAS.md.

## Rutas y contrato

Las rutas derivan de BANK_ROOT o de la carpeta del paquete. La separación de columnas evita incluir target, edad y duration en el estimador.

```{literalinclude} actividad_3/proyecto_inicial/src/bank_ops/config.py
:language: python
:linenos:
```

## Snapshot y validación

load verifica huella y cantidad de filas antes de asignar row_id. partitions conserva orden. download es una acción explícita, nunca parte de inferencia ni pruebas.

```{literalinclude} actividad_3/proyecto_inicial/src/bank_ops/data.py
:language: python
:linenos:
```

## Entrenamiento y métricas

Pipeline conserva transformaciones y modelo. train crea versiones inmutables; read_model comprueba integridad antes de cargar un artefacto propio.

```{literalinclude} actividad_3/proyecto_inicial/src/bank_ops/model.py
:language: python
:linenos:
```

## API instrumentada

create_app crea métricas por instancia y carga el modelo durante startup. Readiness detecta falta de artefacto; cada respuesta informa versión e identificador. El log es local y usa un worker.

```{literalinclude} actividad_3/proyecto_inicial/src/bank_ops/api.py
:language: python
:linenos:
```

## Drift, etiquetas y grupos

Los reportes se calculan fuera de la API. Se rechazan uniones duplicadas y se informa cobertura. Tasas sin denominador suficiente no se presentan como conclusiones sólidas.

```{literalinclude} actividad_3/proyecto_inicial/src/bank_ops/monitor.py
:language: python
:linenos:
```

## Actualización

El proyecto inicial entrega promoción y rollback, pero exige implementar la política compare. Revisar contrato de retorno y tolerancias de la actividad.

```{literalinclude} actividad_3/proyecto_inicial/src/bank_ops/lifecycle.py
:language: python
:linenos:
```

## Interfaz de comandos

La misma CLI se utiliza desde terminal, Docker y CI; la lógica de negocio no se duplica en YAML.

```{literalinclude} actividad_3/proyecto_inicial/src/bank_ops/cli.py
:language: python
:linenos:
```

## Descarga

{download}`Proyecto inicial completo <descargas/proyecto_inicial.zip>`. Descomprimir y usar esa carpeta como raíz del repositorio de la actividad.
