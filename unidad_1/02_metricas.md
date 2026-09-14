# Seguimiento del desempeño en producción

## Tres capas de medición

La infraestructura informa si el servicio responde: disponibilidad, latencia, errores y saturación. Las métricas del modelo evalúan su capacidad predictiva: discriminación, calibración y errores por clase. Las del proceso miden impacto: contactos útiles, tiempos y costos. Ninguna capa reemplaza a las otras: una API rápida puede servir un modelo inútil.

En clasificación desbalanceada la accuracy puede ser alta prediciendo siempre la clase mayoritaria. La precisión positiva es TP/(TP+FP); el recall es TP/(TP+FN). F1 resume ambas, pero oculta sus costos. ROC AUC mide ordenamiento entre positivos y negativos; average precision (AP) resume precisión-recall a distintos umbrales y debe interpretarse junto a la prevalencia. Brier es el promedio de (p−y)²: menor es mejor y evalúa probabilidades.

![Comparación de escenarios](../images/desempeno.png)

El umbral 0.25 es una política educativa fija. No significa que 0.25 sea óptimo para una campaña real. Elegirlo requeriría costos de contacto, capacidad y consecuencias para los grupos. Cambiar el umbral también es un cambio del sistema y debe versionarse.

## Etiquetas tardías

Una predicción se registra con `prediction_id`, instante y versión. Cuando llega su resultado se une por identificador, no por orden de fila. La cobertura de etiquetas es observadas/emitidas; si solo llegan resultados de ciertos casos, la evaluación puede estar sesgada.

```python
import pandas as pd
from bank_ops.monitor import delayed_performance
pred = pd.DataFrame({"prediction_id":["a","b","c"],
    "probability":[.8,.1,.4], "model_version":["v1","v1","v1"]})
labels = pd.DataFrame({"prediction_id":["a","b"], "target":[1,0]})
print(delayed_performance(pred, labels))
```

El tercer registro no es un negativo: es un caso sin resultado. La función conserva el denominador de cobertura, rechaza identificadores duplicados y separa versiones. Si una ventana contiene una sola clase, AUC no está definida y se devuelve `None`; no se inventa cero.

## Ventanas y objetivos
Un objetivo didáctico puede exigir p95 menor de 500 ms y readiness disponible durante una prueba. En producción se debe fijar población, periodo, exclusiones y presupuesto de error. Medir p95 sobre tres peticiones no demuestra capacidad. Tampoco comparar métricas de dos ventanas con prevalencias muy distintas prueba que el cambio se deba al modelo.

**Ejercicio:** una ventana tiene AP menor pero mayor prevalencia, y solo 40 % de etiquetas. Redacte qué investigaría antes de declarar un incidente del modelo.

<!-- MANUAL AVANZADO -->

## Del score a la decisión operativa

Un clasificador genera un score $s(x)$; un umbral $\tau$ produce $\hat y=\mathbb{1}[s(x)\geq\tau]$. Son dos objetos que se evalúan de manera diferente. Cambiar $\tau$ altera precisión, recall y volumen de decisiones positivas, pero no cambia el orden de los scores y por tanto no modifica las métricas de ranking cuando las entradas y etiquetas permanecen iguales. Separar estos niveles permite distinguir un problema del modelo de un problema de política de decisión.

En Bank Marketing, «positivo» significa suscripción observada en el conjunto histórico. No significa beneficio causal de realizar una llamada: los datos no contienen el resultado contrafactual de no contactar a la misma persona en las mismas condiciones. Una política comercial real necesitaría información adicional sobre costos, capacidad de contacto y efectos de la intervención. El ejercicio de utilidad que sigue es un supuesto educativo para comparar decisiones, no una estimación de rentabilidad bancaria.

La matriz de confusión debe conservar su convención. El proyecto usa filas de clase real y columnas de clase predicha: `[[TN, FP], [FN, TP]]`. Si alguien interpreta el segundo elemento como FN, obtiene explicaciones incorrectas aunque el cálculo sea válido. Presentar denominadores junto a las tasas hace más fácil auditar qué se está contando.

### Un ejemplo con números completos

Suponga 1 000 casos con 100 positivos reales. El modelo identifica 60 de ellos y marca también 140 negativos como positivos. Entonces TP=60, FN=40, FP=140 y TN=760. La precisión es 60/200=0.30, el recall es 60/100=0.60 y la accuracy es 820/1 000=0.82. Un clasificador que siempre diga «no» alcanzaría accuracy 0.90, pero no recuperaría ninguna suscripción. Esto no convierte automáticamente al primero en útil: exige valorar si los 60 casos recuperados justifican los 200 contactos propuestos.

Con un valor hipotético de 10 unidades por verdadero positivo y costo de 2 unidades por cada decisión positiva, la utilidad sería $10TP-2(TP+FP)=200$. Si el valor baja a 5, la utilidad pasa a -100. El mismo modelo y la misma matriz conducen a decisiones económicas diferentes. Ninguno de esos valores constituye una tarifa real; el objetivo es hacer explícita la sensibilidad del criterio.

## Discriminación y prevalencia

ROC AUC resume ordenamiento entre pares positivos y negativos. AP resume precisión a lo largo de incrementos de recall y es especialmente informativa cuando interesa la calidad de las primeras selecciones. No son unidades intercambiables. La AP de una referencia aleatoria se relaciona con la prevalencia, por lo que comparar AP de dos poblaciones con distinta proporción de positivos requiere contexto. La función del proyecto devuelve `None` para AUC y AP cuando no hay ambas clases; es una decisión conservadora de reporte que evita resultados difíciles de interpretar. [Definiciones de métricas en scikit-learn 1.6](https://scikit-learn.org/1.6/modules/model_evaluation.html).

Considere dos ventanas con el mismo comportamiento condicional del clasificador, pero con prevalencias diferentes. La proporción de positivos entre los casos seleccionados puede cambiar sin que haya cambiado el ranking relativo. Además, una campaña puede modificar qué clientes reciben seguimiento. Las etiquetas observadas dejan entonces de representar exactamente la población de inferencia. Por eso las tablas del monitoreo deben mostrar n, prevalencia, cobertura y versión junto a cada métrica.

La estabilidad de AUC tampoco garantiza estabilidad en la zona relevante de la curva. Si solo pueden contactarse 100 personas, interesa el desempeño entre las primeras 100, la distribución de scores cerca del punto de corte y la robustez de esa selección. Una mejora en regiones que nunca reciben una acción puede elevar una métrica global sin cambiar el resultado operativo.

## Calibración: cuando 0.20 pretende significar veinte por ciento

Un modelo calibrado asigna probabilidades coherentes con frecuencias observadas en conjuntos comparables. Esto se analiza agrupando scores y comparando promedio predicho con proporción positiva. Los intervalos deben mostrar cuántas observaciones contienen; un punto basado en ocho casos no merece la misma confianza que uno basado en ochocientos. Una curva de calibración no prueba calibración individual y puede ocultar diferencias entre grupos.

El Brier binario es $\frac1n\sum_i(p_i-y_i)^2$. Evalúa error probabilístico, pero no es una medida exclusiva de calibración: también depende de la capacidad de separar casos y de la incertidumbre de la población. Usarlo como condición de aceptación junto con ranking evita confundir dos propiedades diferentes. Los métodos de recalibración deben ajustarse con datos distintos de los usados para medir el resultado final. [Guía de calibración de scikit-learn](https://scikit-learn.org/stable/modules/calibration.html).

```python
# Ejemplo autónomo: una transformación monótona conserva el ranking.
import numpy as np
from sklearn.metrics import roc_auc_score, brier_score_loss
y = np.array([0, 0, 1, 1, 0, 1])
p = np.array([.1, .2, .6, .8, .3, .7])
q = p ** 3
assert roc_auc_score(y, p) == roc_auc_score(y, q)
print(brier_score_loss(y, p), brier_score_loss(y, q))
```

La potencia conserva el orden de probabilidades positivas, pero cambia su escala y puede deteriorar Brier. No se recomienda elevar probabilidades al cubo: el contraejemplo demuestra por qué un único número de ranking no describe toda la calidad de un predictor probabilístico.

## Selección de umbral y capacidad

El notebook 02 amplía el baseline con una tabla de umbrales. Para cada umbral se calculan TP, FP, FN, TN, proporción seleccionada y utilidad hipotética. El entrenamiento solo utiliza train; el análisis de políticas se realiza sobre validation. Después se congela una decisión antes de cualquier evaluación final. Elegir repetidamente el mejor umbral sobre test transforma ese conjunto en otra validación y destruye su función como comprobación independiente.

Una restricción de capacidad puede escribirse como $\sum_i\mathbb{1}[p_i\geq\tau]\leq B$, donde B es el presupuesto de acciones para el lote. Si el volumen de entrada aumenta, un umbral fijo puede dejar de satisfacerla. Una política top-k respeta una capacidad fija, pero su umbral efectivo cambia con la población. Las dos estrategias deben compararse según el proceso real, incluyendo empates, prioridades y personas que podrían quedar sistemáticamente excluidas.

El baseline del material puede producir recall cero al umbral 0.25. Esa salida no se corrige ocultándola ni forzando un candidato a ser mejor. Se estudia la distribución de scores, se comparan umbrales en validación y se documenta que la política inicial no recupera positivos. El gate actual tolera diferencias frente al vigente; si ambos tienen recall cero, esa condición por sí sola no garantiza un nivel absoluto útil. Una política industrial añadiría mínimos absolutos justificados.

## Incertidumbre y comparación justa

Un cambio de 0.002 en AP no tiene el mismo significado con 30 positivos que con 3 000. Para comparar dos modelos sobre las mismas filas, un bootstrap pareado reutiliza los mismos índices en ambos. Así se analiza la distribución de la diferencia y se conserva la dependencia entre sus errores. Muestrear cada modelo con índices independientes añadiría variabilidad que no corresponde a esa comparación.

El bootstrap simple supone unidades aproximadamente independientes. Si existen varias solicitudes por persona o bloques temporales correlacionados, conviene remuestrear personas o bloques; Bank Marketing no facilita un identificador de persona suficiente para demostrar esa estructura. El notebook declara esta limitación y no presenta un intervalo exploratorio como certificación de producción. También registra remuestras que no contienen ambas clases, en lugar de convertir métricas indefinidas en ceros.

Compare siempre sobre el mismo conjunto, las mismas etiquetas, el mismo contrato y una política de umbral documentada. Si se recalibra un candidato, la recalibración forma parte del candidato: necesita sus datos de ajuste, versión y evaluación. No debe añadirse después de observar test y continuar llamando independiente a la comparación.

## Ejercicio con interpretación

Una ventana tiene AP menor, AUC parecida y prevalencia mucho menor; otra conserva AP, pero duplica los contactos necesarios para recuperar veinte positivos. Escriba una hipótesis y una comprobación para cada caso. Después explique qué métrica comunicaría al responsable de capacidad y cuál al equipo que estudia probabilidades.

```{admonition} Orientación para revisar la respuesta
:class: dropdown
En la primera ventana hay que comprobar cuánto de la diferencia se relaciona con prevalencia y selección de etiquetas antes de concluir deterioro. En la segunda interesa medir precisión y carga de trabajo en el punto operativo. Una métrica global estable no asegura que el presupuesto se conserve. Ninguna respuesta está completa sin tamaños y definición de población.
```

La ficha final de seguimiento debe permitir reconstruir una afirmación: «para esta versión, sobre esta cohorte y estas etiquetas maduras, se observaron estas tasas con estos denominadores». Un dashboard que muestra únicamente «accuracy: 92 %» no permite decidir si el servicio está mejorando, si el problema cambió o si simplemente faltan los resultados difíciles.
