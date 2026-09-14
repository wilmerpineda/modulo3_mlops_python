# Autoevaluación con retroalimentación

Responda antes de desplegar las soluciones. Estas preguntas son formativas y no sustituyen la actividad en equipo.

1. **¿Data drift implica peor modelo?** No. Señala un cambio en X; el impacto predictivo necesita evidencia adicional.
2. **¿AUC de una ventana con solo negativos es cero?** No está definida. Reportar ausencia de ambas clases y denominadores.
3. **¿Un 200 en health demuestra readiness?** No. El proceso puede vivir sin artefacto cargado.
4. **¿Cada prediction_id debe ser una etiqueta de Prometheus?** No. Generaría series sin límite; usar registros para identificación.
5. **¿Un candidato que entrena sin error debe promoverse?** No. Comparar métricas, compatibilidad, segmentos y revisión.
6. **¿Un cron garantiza ejecución exacta?** No. La infraestructura puede retrasarlo; registrar ejecución y permitir activación manual.
7. **¿Cambiar current.json actualiza un proceso vivo?** No en este ejemplo. Reiniciar y comprobar versión servida.
8. **¿Excluir edad garantiza equidad?** No. Persisten proxies y sesgos en selección y etiquetas.
9. **¿Un test final usado para elegir umbral sigue siendo test?** Se convirtió en parte de la selección. Reservar evaluación independiente.
10. **¿El hash protege contra cualquier manipulación?** No si pueden modificar archivo y manifiesto; requiere confianza en la referencia.
11. **¿El contenedor ve las promociones realizadas fuera de él?** No: sus volúmenes son otro registro salvo montaje explícito.
12. **¿No recibir etiqueta equivale a no suscribir?** No. Es un resultado pendiente y debe afectar cobertura, no inventar clase.

## Retos adicionales

- Añadir un análisis bootstrap con intervalos de TPR por grupo y explicar sus supuestos.
- Implementar alerta de drift persistente por lotes con tamaño mínimo, sin promoción automática.
- Diseñar una liberación canary y sus criterios de cancelación, sin exigir infraestructura de pago.
- Comparar latencia con uno y varios workers, adaptando antes la instrumentación multiproceso.

## Lista de revisión personal
Puedo identificar el snapshot y commit; explicar el momento de predicción; diagnosticar un 503; distinguir drift de degradación; leer el dashboard; ejecutar el CI; justificar un rechazo; recuperar una versión y comunicar límites de equidad.

<!-- MANUAL AVANZADO -->

## Cómo utilizar los casos avanzados

Resuelva cada caso antes de abrir la orientación. Escriba cuatro elementos: observación, hipótesis, comprobación y decisión provisional. No es necesario acertar una causa única cuando la información no la determina. Una respuesta profesional puede concluir que falta evidencia, siempre que identifique cuál y cómo obtenerla. Estos casos son formativos y no modifican la rúbrica de la actividad en equipo.

Puede autoevaluarse con una escala de tres niveles: identifica el síntoma; conecta el síntoma con una comprobación; o además delimita incertidumbre y consecuencias de actuar. La respuesta más extensa no es necesariamente mejor. Se valora que cada afirmación esté respaldada y que no se mezclen contrato, calidad predictiva y disponibilidad.

## Caso 1. Un detector encuentra cambio en una muestra enorme

Balance presenta KS con p-valor muy pequeño, pero la distancia normalizada es reducida. No hay cambios de versión ni errores de captura conocidos. El responsable pide reentrenar inmediatamente. Explique qué concluye del contraste, qué información falta sobre impacto y cómo evaluaría la política de alertas en periodos estables.

```{admonition} Orientación del caso 1
:class: dropdown
El contraste aporta evidencia contra igualdad bajo sus supuestos; no mide costo ni prueba deterioro. El gran volumen permite detectar diferencias pequeñas. Revisar magnitud, distribución, segmentos y desempeño con etiquetas maduras. Evaluar falsas alarmas y tiempo de detección antes de decidir un umbral operativo. Reentrenar puede producir un candidato, pero la señal no autoriza automáticamente promoverlo.
```

## Caso 2. Todas las columnas parecen estables

Las distribuciones marginales de dos features binarias no cambiaron, pero un modelo que utiliza su interacción empeoró. Proponga una construcción de referencia y actualidad que haga posible esa situación. Después explique qué detector adicional estudiaría y cómo evitaría que aprenda un identificador artificial de origen.

```{admonition} Orientación del caso 2
:class: dropdown
Parejas (0,0)/(1,1) frente a (0,1)/(1,0) conservan marginales y cambian asociación. Estudiar interacciones relevantes o un clasificador de dominio con evaluación separada. Excluir nombres de archivo, índices que revelen la partición y otras fugas. La separabilidad de dominio no demuestra por sí sola la causa del deterioro ni sustituye las etiquetas.
```

## Caso 3. La AP sube mientras la población cambia

En el escenario con etiquetas invertidas, AP puede aumentar y Brier empeorar. Un integrante escribe que el modelo mejoró porque AP es mayor. Revise la afirmación considerando prevalencia, significado de Y y comparabilidad. Indique qué resultado del detector de entradas esperaría si recibe solo FEATURES.

```{admonition} Orientación del caso 3
:class: dropdown
La inversión modifica la relación y la prevalencia. AP no debe compararse como si fueran poblaciones idénticas. Brier aporta otra dimensión del error probabilístico. El detector de features no observa la intervención en Y porque X permanece igual. La conclusión es sobre una simulación extrema, no sobre una mejora real del sistema ni sobre drift histórico demostrado en UCI.
```

## Caso 4. Cero errores y target ausente

El panel de porcentaje muestra cero, pero Prometheus informa `up=0`. El último punto de predicciones por clase tiene veinte minutos. Explique por qué no es correcto afirmar que el sistema opera sin errores. Diseñe una comprobación desde el servicio hasta Grafana y describa qué estados debe distinguir el panel.

```{admonition} Orientación del caso 4
:class: dropdown
Puede faltar recolección, no errores. Comprobar API, endpoint metrics, target, consulta y fuente de Grafana. Diferenciar cero eventos, tráfico bajo, dato antiguo y ausencia del target. Un respaldo numérico para una serie 5xx no debe ocultar pérdida de observabilidad. La recuperación requiere verificar servicio y frescura de datos.
```

## Caso 5. El umbral relativo acepta un modelo inútil

Vigente y candidato tienen recall cero con umbral 0.25. El candidato cumple las tolerancias relativas y otro integrante afirma que está listo para producción. Distinga elegibilidad de utilidad absoluta y proponga una investigación que conserve intacto el conjunto de prueba.

```{admonition} Orientación del caso 5
:class: dropdown
No deteriorarse respecto de un baseline débil no asegura utilidad. Analizar scores, umbrales y capacidad en validation; discutir mínimos absolutos y contexto antes de aprobar. No cambiar el gate retrospectivamente para favorecer un resultado ni optimizar con test. La réplica equivalente sirve para probar transición, no para demostrar mejora.
```

## Caso 6. Promoción en disco, otra versión en memoria

`current.json` apunta a candidate-v2, pero `/model/metadata` devuelve baseline-v1 y readiness es 200. Enumere dos explicaciones compatibles con el diseño local y describa qué evidencia confirmaría una promoción completa. Incluya el caso de registros separados entre Python y Compose.

```{admonition} Orientación del caso 6
:class: dropdown
La API puede no haberse reiniciado o la consulta puede apuntar a otro entorno. El modelo se carga al arrancar, y los volúmenes de Compose son distintos de las carpetas locales. Confirmar registro, host, puerto, reinicio, versión HTTP y predicción válida. Readiness demuestra capacidad inicial con algún modelo cargado, no identidad con el puntero que se inspeccionó en otro lugar.
```

## Caso 7. Un CI verde con una tarea pendiente

GitHub Pages está verde, el CI del starter usa compileall y existe un test omitido. El equipo presenta esas capturas como prueba de recuperación automatizada. Identifique exactamente qué se ha comprobado y qué evidencia adicional exige A3-02 y A3-03.

```{admonition} Orientación del caso 7
:class: dropdown
Pages comprobó compilación y publicación de documentación. Compileall comprobó compilación sintáctica. Falta ejecutar pytest con la prueba de transición implementada, mostrar rechazo y recuperación con versión HTTP, y conservar fallo deliberado y reparación del CI de ML. Los workflows anidados no se ejecutan hasta colocarlos en la raíz del repositorio de actividad.
```

## Caso 8. Una tasa idéntica con evidencia desigual

Dos grupos tienen TPR 0.60; uno cuenta con cinco positivos y otro con quinientos. Sus prevalencias son diferentes. Explique por qué no puede afirmarse igualdad demostrada y por qué la selección puede diferir aunque las tasas condicionales coincidan. Indique cómo presentaría un grupo sin positivos.

```{admonition} Orientación del caso 8
:class: dropdown
La incertidumbre es mucho mayor con cinco positivos. Mostrar denominadores e intervalos apropiados, sin tratar intervalos individuales como prueba automática de una diferencia. Selección depende de TPR, FPR y prevalencia. Sin positivos, TPR es indefinida. La ausencia de denominador no se convierte en cero ni en evidencia de equidad.
```

## Caso 9. Una prueba de carga parece escalar mal

Con cuatro clientes, throughput apenas mejora y p95 aumenta. El CPU del cliente también está alto. El equipo propone cuatro réplicas de API. Revise la inferencia considerando el diseño del generador, conexiones, carga cerrada, escritura local y memoria del modelo.

```{admonition} Orientación del caso 9
:class: dropdown
El cuello de botella puede estar en cliente, servicio, conexiones o una sección serial. Medir recursos y controlar condiciones antes de atribuirlo a capacidad del estimador. Más réplicas requieren almacenamiento y observabilidad coherentes; un lock de hilos no coordina procesos. La prueba no estima una tasa externa fija y puede reducir llegadas cuando el servicio se ralentiza.
```

## Caso 10. Integridad sin fuente confiable

Un archivo joblib y su manifiesto descargados de una fuente desconocida tienen hashes coincidentes. Un operador propone cargarlos porque «pasaron seguridad». Distinga integridad, autenticidad y riesgo del formato. Después explique cómo un cambio de finales de línea puede afectar el snapshot sin cambiar sus valores tabulares.

```{admonition} Orientación del caso 10
:class: dropdown
La coincidencia solo confirma contenido respecto de esa referencia; si ambos provienen de una fuente no confiable, no hay autenticidad establecida. Joblib puede ejecutar código al cargar objetos. Los hashes operan sobre bytes: CRLF y LF producen huellas distintas. Investigar discrepancias y proteger la fuente de referencia; no recalcular automáticamente para aceptar cualquier cambio.
```

## Caso integrador: campaña, etiquetas y actualización

Una campaña nueva duplica tráfico, aumenta la categoría `unknown`, reduce cobertura de etiquetas y eleva p95. El bosque candidato mejora una métrica puntual en validation, pero consume más memoria. Prepare un orden de investigación y un criterio provisional de promoción. Separe acciones urgentes del servicio, revisión de captura, maduración de etiquetas y evaluación del candidato.

Una respuesta sólida comienza por mantener observabilidad y capacidad de atención, comprueba si `unknown` refleja un contrato roto y evita entrenar automáticamente sobre captura defectuosa. Después analiza cobertura comparable y capacidad del candidato. La promoción necesita evidencia de compatibilidad y recuperación, no solo una métrica favorable. Si el servicio se recupera pero faltan resultados, el impacto predictivo puede seguir abierto.

## Mapa de retorno al libro

| Si le costó… | Vuelva a… | Evidencia que debería poder producir |
|---|---|---|
| Separar señal e impacto | Unidad 1 y notebooks 01–04 | Tabla con población, medida y límite |
| Diagnosticar ausencia de datos | Unidad 2 | Consulta, target, tiempo y explicación |
| Justificar transición | Unidad 3 y notebook 06 | Comparación y versiones HTTP |
| Interpretar un workflow | Unidad 4 | Recorrido de entrada a artefacto |
| Evaluar pruebas y grupos | Unidad 5 y notebook 05 | Propiedad probada y denominadores |
| Recomendar capacidad | Unidad 6 | Experimento controlado y presupuesto |

El dominio del módulo no consiste en recordar comandos aislados. Consiste en conectar un síntoma con evidencia, reconocer qué no está identificado y elegir una acción cuya consecuencia pueda comprobarse. Conserve una respuesta inicial y otra después del laboratorio para observar cómo cambió su razonamiento.
