# Sesgos y equidad en modelos desplegados

## Más allá de una métrica global

Un promedio aceptable puede ocultar errores concentrados. El dataset refleja decisiones históricas de contacto, registro y respuesta; no es una muestra neutral de todas las personas. Sesgo de selección, medición y etiquetas puede persistir aunque el algoritmo no use explícitamente edad.

El laboratorio compara grupos de 18–29, 30–59 y 60–100 años. Son segmentos pedagógicos, no una clasificación legal ni una definición universal de grupos protegidos. La selección de grupos en una aplicación real requiere contexto y participación de responsables.

## Qué calcular
Tasa de selección = proporción con decisión positiva. TPR = positivos reales identificados; FPR = negativos reales contactados como positivos. Comparar TPR se relaciona con igualdad de oportunidad; comparar simultáneamente TPR y FPR corresponde a otra exigencia. Paridad de selección puede entrar en tensión con diferencias de prevalencia y calibración.

```python
from bank_ops.monitor import fairness
from bank_ops.config import FEATURES
probability = estimator.predict_proba(test[FEATURES])[:, 1]
rows = fairness(test, probability, threshold=0.25)
```

![Auditoría por grupos](../images/equidad.png)

Se informa n, positivos y negativos junto a las tasas. Si un grupo no tiene positivos, TPR no se define. El indicador `reliable` requiere al menos 30 positivos y 30 negativos como advertencia mínima docente; no constituye un análisis de potencia ni intervalo de confianza. Para decisiones reales, añadir incertidumbre y análisis de intersecciones cuando el volumen lo permita.

## Mitigación y evaluación
Investigar primero cobertura, calidad y disponibilidad de etiquetas. Recolectar datos de grupos subrepresentados puede ser más útil que ajustar un umbral. Cambiar umbrales por grupo tiene implicaciones técnicas y normativas que requieren revisión contextual; no se automatiza aquí. Evaluar si una mitigación mejora una brecha pero perjudica otra métrica o grupo.

**Ejercicio:** elija una diferencia observada, reporte los denominadores, formule dos causas posibles y proponga una comprobación. No use la palabra «justo» como conclusión basada únicamente en una tabla.
