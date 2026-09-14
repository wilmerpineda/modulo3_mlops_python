# Referencias, umbrales y calidad de datos

## Diseñar una comparación válida

La referencia es una población de comparación, no necesariamente todos los datos de entrenamiento. Puede ser validación aceptada, un periodo operativo estable o una ventana móvil. Una referencia fija revela desviaciones acumuladas; una móvil se adapta a estacionalidad, pero puede normalizar lentamente un deterioro. Versionar la referencia, tamaño, selección de columnas y fecha de aprobación.

Antes de medir drift hay que verificar esquema, nulos, dominios, rangos y volumen. Una columna llena de nulos o un lote vacío no es una evidencia estadística utilizable. Los duplicados requieren reglas de negocio: dos filas idénticas pueden ser contactos distintos. Sin identificador no se deben borrar automáticamente.

```python
from bank_ops.data import validate
validate(stable)
invalid = stable.copy()
invalid.loc[invalid.index[0], "campaign"] = -3
try:
    validate(invalid)
except ValueError as error:
    print("Lote rechazado:", error)
```

## Métodos y cautelas

Una prueba KS compara funciones de distribución acumulada de una variable continua. Un p-valor es evidencia contra una hipótesis nula bajo supuestos, no el tamaño del cambio. Con muchas filas pueden resultar significativos cambios pequeños. La distancia de Wasserstein mide desplazamiento y depende de las unidades. Para categorías se pueden comparar proporciones; categorías raras y nuevos niveles merecen atención.

PSI resume cambios entre histogramas mediante Σ(actual−referencia)·log(actual/referencia). Depende de los bins y necesita tratamiento de ceros. Sus umbrales populares no son leyes universales. Evaluar múltiples columnas aumenta la probabilidad de falsas alertas; inspeccionar persistencia, importancia, tamaño del cambio y contexto.

![Cambio controlado de balance](../images/distribuciones.png)

## Política operativa didáctica
Separar alertas informativas de incidentes. Una violación de contrato rechaza el lote. Un cambio de distribución abre investigación. Una degradación sostenida con suficientes etiquetas activa comparación de candidatos. El laboratorio guarda reportes de Evidently; no conecta automáticamente toda señal de drift con una promoción.

Para diseñar umbrales, repetir ventanas estables, medir falsos positivos y simular cambios conocidos. Documentar tamaño mínimo y tiempo de persistencia. El módulo usa controles estables de una misma ventana para aislar ese experimento y mantiene la evaluación histórica final separada.

**Ejercicio:** comparar una muestra de 100 filas y otra de 1500. Explicar por qué una conclusión puede cambiar sin que la diferencia de medias cambie sustancialmente.

<!-- MANUAL AVANZADO -->

## Diseñar una referencia que conserve significado

La referencia no es necesariamente el conjunto de entrenamiento completo. Puede ser un periodo aceptado de producción, una muestra congelada y estratificada, o un conjunto estacional comparable. Cada elección responde a una pregunta diferente. Comparar contra entrenamiento pregunta cuánto se alejó el uso actual del soporte conocido; comparar contra la semana anterior pregunta qué cambió recientemente. Ninguna sustituye a la otra.

Una referencia fija facilita comparar la magnitud de señales a lo largo del tiempo y reproducir incidentes. Su costo es perder representatividad cuando el negocio evoluciona de manera legítima. Una referencia móvil se adapta, pero puede normalizar lentamente un deterioro: después de varias semanas, tanto referencia como actualidad contienen el mismo problema. Un diseño práctico conserva una referencia aprobada y otra reciente, indicando claramente cuál alimenta cada métrica.

La actualización de la referencia es una decisión versionada. Debe registrar quién aceptó el nuevo periodo, qué calidad y resultados se observaron, qué exclusiones se aplicaron y desde cuándo cambia la interpretación. Reemplazarla para apagar una alarma elimina información sobre el incidente. Tampoco se deben escoger retrospectivamente ventanas que produzcan la conclusión deseada.

## Tiempo de evento, de recepción y de evaluación

Una predicción puede producirse el lunes, recibir una etiqueta el jueves e ingresar al almacén el viernes. Hay al menos tres tiempos distintos. Si se agrupa por recepción de la etiqueta, una campaña con resultados tardíos aparecerá artificialmente como actividad del viernes. Para evaluar una cohorte se necesita el tiempo de la predicción y una fecha de corte que determine qué etiquetas eran conocidas.

La cobertura de una cohorte a la fecha t es $C(t)=N_{\text{etiquetados a }t}/N_{\text{predicciones de la cohorte}}$. Su valor evoluciona. Comparar la cohorte de ayer con una de hace un mes puede comparar resultados inmaduros con maduros, aunque las tasas se calculen correctamente. Conviene presentar curvas de maduración o evaluar cohortes con el mismo horizonte, por ejemplo resultados conocidos siete días después de cada predicción. El horizonte debe derivarse del proceso, no de la comodidad del dashboard.

En el material, el log de API incluye hora UTC de predicción, pero el CSV básico de etiquetas contiene solo identificador y target. Por tanto, la función de unión demuestra cobertura y métricas por versión; no implementa reconstrucción histórica completa «a fecha de». El notebook 04 crea tiempos y patrones de observación sintéticos para estudiar esa limitación. Añadir un timestamp a un ejemplo no convierte las fechas incompletas del dataset UCI en una cronología real.

## Ventanas fijas, móviles y por volumen

Una ventana diaria es fácil de comunicar y permite asociar campañas o cambios de configuración. Su tamaño varía si el tráfico cambia. Una ventana de las últimas 2 000 solicitudes mantiene volumen, pero puede representar diez minutos en hora pico y varios días en periodos tranquilos. Una ventana móvil suaviza fronteras artificiales, aunque induce dependencia entre evaluaciones consecutivas.

Suponga un cambio a las 23:50. Una ventana del día completo puede diluirlo entre muchas observaciones anteriores; una ventana corta lo detectará antes, pero contendrá menos datos. Puede combinarse una vista rápida de calidad con una evaluación más lenta de desempeño. Lo importante es que el tiempo de respuesta exigido y la incertidumbre sean compatibles. No hay una duración universal óptima.

| Diseño | Ventaja | Riesgo que debe declararse |
|---|---|---|
| Periodo fijo | Facilita comparar campañas y cierres | Volumen desigual y efectos de frontera |
| Últimos N casos | Controla tamaño observado | Duración variable y mezcla de contextos |
| Ventana deslizante | Actualiza señales con frecuencia | Solapamiento y falsa impresión de replicación |
| Cohorte madura | Alinea disponibilidad de resultados | Retrasa confirmación de pérdida predictiva |
| Referencia estacional | Reduce comparaciones inadecuadas | Requiere historia y contexto suficientes |

Una política mínima especifica frecuencia de cálculo, longitud de ventana, mínimo de casos, mínimo de positivos y fecha de corte de etiquetas. Si un requisito falla, el resultado debe ser «evidencia insuficiente» o «evaluación pendiente», no verde automático. Esa distinción permite diferenciar un sistema estable de uno que dejó de recibir datos.

## Contratos antes de estadísticas

El contrato incluye esquema, dominio, unidades, significado y disponibilidad temporal. `balance` puede llegar como número válido y aun así cambiar de euros a centavos; una columna de edad puede conservar el nombre mientras cambia de años a meses. Las validaciones de tipos no detectan esos errores semánticos. Un contrato documentado identifica quién produce cada variable y cómo se verifican cambios de significado.

En el proyecto se revisan columnas requeridas, rangos y valores permitidos, y se excluye duration por disponibilidad posterior a la llamada. La API además rechaza campos extra. Esta combinación protege varias fronteras, pero no certifica que todo registro aceptado represente una persona válida. La categoría `unknown` es un valor explícito, no equivale a un nulo técnico. Un aumento de `unknown` puede revelar pérdida de información aunque el lote supere todas las validaciones sintácticas.

Una política de rechazo debe definir granularidad. Rechazar un lote completo conserva integridad cuando la falla afecta su significado, pero puede interrumpir casos correctos. Aislar filas defectuosas permite continuidad, aunque cambia la población analizada y requiere informar tasas de exclusión. No se deben calcular métricas después de eliminar silenciosamente los registros más difíciles. El laboratorio rechaza determinadas entradas para hacer visibles esas decisiones.

## Dos sesgos que una unión correcta no elimina

Primero, las etiquetas pueden faltar de manera relacionada con el resultado. Si las suscripciones exitosas se registran rápido y los rechazos tarde, el desempeño observado al principio parecerá distinto del final. Segundo, la política del modelo puede determinar quién recibe una acción y por tanto quién puede obtener una etiqueta. Un sistema que solo observa clientes contactados no puede evaluar directamente a todos los no contactados.

La unión por identificador debe ser uno a uno, sin duplicados que multipliquen filas. Pero incluso una unión técnicamente perfecta puede ser estadísticamente sesgada. Informar cobertura por score, segmento y versión ayuda a diagnosticar el mecanismo de observación. No se recomienda rellenar etiquetas ausentes con cero: eso impone un resultado no observado y contamina tanto la evaluación como el siguiente entrenamiento.

Un análisis más avanzado podría ponderar casos por probabilidad de observación, pero requiere supuestos sobre ese mecanismo, soporte suficiente y pesos controlados. Si un grupo nunca recibe etiqueta, ninguna ponderación crea resultados que no existen. En este módulo se prioriza mostrar el sesgo y formular la necesidad de datos adicionales, antes de introducir una corrección automática difícil de justificar.

## Protocolo para calibrar una alarma

Seleccione varias ventanas históricas consideradas aceptables y reserve otras para comprobar la política. Estime la distribución de la medida de cambio bajo variaciones normales. Introduzca perturbaciones relevantes para el contrato: unidades, categorías desconocidas, cambios de mezcla y pérdida de campos. Evalúe sensibilidad y falsas alarmas con la misma regla que se usaría después. No elija el umbral con el único incidente que desea demostrar.

Después incluya costos operativos: tiempo de revisión por alerta, daño de esperar y capacidad de atención. Una alerta diaria puede ser sostenible para un servicio crítico; veinte por hora quizá no lo sean. Registre versiones de detector, referencia y política para que el cambio de frecuencia de alertas pueda atribuirse a datos o a configuración. Si todo cambia a la vez, la serie histórica pierde comparabilidad.

El criterio del proyecto de dos ventanas y volumen mínimo es una tarea pedagógica: el equipo debe justificar sus valores mediante evidencia del experimento. No se exige construir un sistema de streaming ni demostrar estacionalidad anual con un CSV sin fechas completas. La calidad de la respuesta depende de reconocer qué inferencias admite el caso disponible.

## Caso de diagnóstico y lectura conectada

Una alerta aparece justo después de que la integración comienza a omitir `contact`. El lote se completa rellenando `unknown`, el score medio baja y todavía no hay etiquetas. La primera intervención debe inspeccionar la integración y cuantificar pérdida de información. Reentrenar con esa captura degradada podría enseñar al modelo una representación accidental y convertir una falla temporal en comportamiento persistente.

```{admonition} Pregunta de comprobación
:class: dropdown
¿Basta con restaurar la integración para cerrar el incidente? No. Hay que verificar que el flujo nuevo recuperó el contrato, identificar predicciones hechas durante la falla, evaluar su impacto cuando existan resultados y decidir si deben corregirse registros o acciones. La recuperación técnica y el cierre del impacto tienen tiempos distintos.
```

Continúe con [Evidently](../unidad_2/04_evidently.md) para materializar referencias y reportes, y con [el notebook de etiquetas](../notebooks/04_etiquetas.ipynb) para estudiar cómo la cobertura modifica la interpretación. La lección central es que una ventana no es solo una selección de filas: es una definición explícita de población, tiempo y evidencia disponible.
