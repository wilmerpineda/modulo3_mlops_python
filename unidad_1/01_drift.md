# Cambios en datos, predicciones y conceptos

## Objetivo
Identificar qué distribución cambió y qué se puede concluir con la evidencia disponible.

Un sistema aprende una aproximación a una relación entre entradas X y respuesta Y bajo ciertas condiciones. En operación cambian clientes, canales, reglas del negocio y mecanismos de captura. El término **model drift** suele usarse de forma amplia para hablar de degradación; en este libro se descompone para evitar diagnósticos ambiguos.

| Fenómeno | Cambio | Evidencia necesaria |
|---|---|---|
| Data drift | P(X) | Comparación de entradas entre ventanas |
| Prediction drift | P(Ŷ) | Distribución de scores o clases predichas |
| Concept drift | P(Y\|X) | Etiquetas y análisis de la relación, controlando otras causas |
| Cambio de prevalencia | P(Y) | Etiquetas observadas y política de muestreo |
| Degradación | Métrica empeora | Predicciones vinculadas a resultados reales |

Si aumenta el balance promedio, existe una señal sobre las entradas, pero el modelo podría seguir ordenando correctamente a los clientes. Si el proveedor invierte una codificación, el fallo puede ser calidad de datos y no un cambio natural de población. Si cambia la política comercial, una misma entrada puede relacionarse de otra manera con la suscripción.

```{mermaid}
flowchart LR
 A[Ventana actual] --> B{Calidad válida}
 B -->|No| C[Corregir captura]
 B -->|Sí| D[Comparar distribuciones]
 D --> E{Hay etiquetas}
 E -->|No| F[Investigar y esperar resultados]
 E -->|Sí| G[Evaluar desempeño y segmentos]
 G --> H[Decidir intervención]
```

## Experimento controlado

```python
from bank_ops.data import load, partitions
from bank_ops.monitor import scenario
_, validation, _ = partitions(load())
stable = validation.iloc[:1000].copy()
shifted = scenario(stable, "shift")
print(stable.balance.mean(), shifted.balance.mean())
assert stable.y.equals(shifted.y)
```

Aquí se modifican entradas sin cambiar etiquetas. El experimento no garantiza que el rendimiento se conserve: precisamente permite medir cómo reacciona el modelo. El escenario `degraded` hace lo contrario: mantiene X y altera artificialmente Y. Un detector de entradas puede no detectar esa intervención.

## Patrones temporales
Un cambio abrupto coincide con una nueva fuente o campaña; uno gradual puede aparecer por hábitos; uno recurrente puede ser estacional. Una única comparación no distingue bien esos patrones. Conservar series de ventanas y contexto operativo facilita no confundir estacionalidad con un incidente.

**Ejercicio:** describa dos situaciones donde haya drift sin degradación y una donde caiga el rendimiento sin cambiar las distribuciones marginales. Para cada una, indique qué dato le falta para tomar una decisión.

**Error frecuente:** ordenar reentrenamiento solo porque un p-valor sea pequeño. La acción debe considerar magnitud, impacto, calidad de etiquetas y costo del error.

## Esquema de consulta

![De la señal a la decisión](../images/drift.svg)

Fuente: elaboración propia.
