# Comparación, promoción y rollback

## Política explícita de aceptación

La solución calcula nuevamente las métricas de ambos artefactos sobre la misma validación. No confía únicamente en un JSON con métricas declaradas. El candidato es elegible si AP no cae más de 0.005, recall no cae más de 0.02 y Brier no empeora más de 0.01. Son tolerancias docentes, no límites universales.

Elegibilidad técnica no equivale a aprobación integral. El operador revisa además equidad, latencia, compatibilidad y contexto, y registra responsable y justificación. Los controles estadísticos no sustituyen esa revisión. Si falla el gate, la función de promoción conserva el puntero vigente.

## Puntero y proceso
`current.json` referencia una versión inmutable. La escritura temporal y reemplazo reducen el riesgo de un archivo parcialmente escrito. El registro de auditoría conserva la acción; no es una transacción distribuida ni un log inviolable. La API carga una vez al iniciar, por lo que después de cambiar el puntero se reinicia y se comprueba `/ready` y `/model/metadata`.

```powershell
poetry run python -m bank_ops.cli promote --version candidate-v2 --actor equipo --reason "Validación y revisión de segmentos completadas"
# Reiniciar el proceso de la API y comprobar versión.
poetry run python -m bank_ops.cli rollback --actor equipo --reason "Incidente de latencia después de actualización"
```

Si el candidato no pasa, el primer comando debe fallar. Ese rechazo es evidencia de operación correcta. Para probar mecánicamente una promoción y rollback sin suponer mejora, entrenar una réplica del baseline con otra versión y declarar que se trata de un control equivalente.

## Estrategias de despliegue
Blue-green mantiene dos entornos y conmuta tráfico; canary comienza con una fracción; shadow calcula respuestas sin afectar la decisión real. Todas necesitan observabilidad por versión y un criterio de interrupción. El laboratorio implementa sustitución con reinicio, que puede interrumpir el servicio; las otras estrategias se estudian como ampliaciones.

**Prueba de aceptación:** promover una réplica, comprobar versión servida, revertir y repetir una predicción. Un puntero correcto sin proceso actualizado no demuestra rollback efectivo.

## Esquema de consulta

![Recuperación verificada](../images/rollback.svg)

Fuente: elaboración propia.

<!-- MANUAL AVANZADO -->

## Precondiciones del proyecto inicial

```{important}
La comparación y la promoción sobre un modelo ya vigente requieren completar A3-01. La primera promoción del baseline, cuando aún no existe `current.json`, inicializa el registro sin comparar contra un antecesor. No interpretar ese arranque como un gate de calidad aprobado. Los ejemplos de transición de este capítulo se ejecutan después de completar la tarea.
```

La política actual impone tres tolerancias relativas. Si $\Delta AP=AP_c-AP_i$, exige $\Delta AP\geq-0.005$. Para recall exige $R_c-R_i\geq-0.02$; para Brier, donde menor es mejor, exige $B_c-B_i\leq0.01$. Las direcciones importan tanto como los límites. Los valores son diferencias absolutas, no porcentajes relativos: pasar de AP 0.20 a 0.195 es una caída de 0.005, equivalente a 2.5 % relativo.

Una conjunción exige todas las condiciones. Un candidato que mejora AP pero empeora Brier más de la tolerancia no compensa automáticamente ese incumplimiento con su mejora. Si se quisiera una función ponderada de utilidad, sería otra política y necesitaría justificación previa. La tarea conserva un contrato simple para poder probar límites y rechazo de manera transparente.

## Elegibilidad, aprobación y activación son estados distintos

Elegibilidad técnica significa que la evidencia satisface una política específica. Aprobación agrega revisión de contexto, riesgos y responsabilidades. Activación cambia el estado servido. Verificación comprueba que la activación produjo el resultado esperado. El proyecto registra actor y motivo, pero no autentica al actor ni implementa un sistema formal de aprobaciones. Una cadena escrita por el operador es trazabilidad declarativa, no prueba criptográfica de identidad.

El gate relativo puede aceptar una réplica equivalente y puede no detectar una utilidad absoluta insuficiente. Si el vigente y el candidato tienen recall cero, ambos cumplen una condición de no deterioro y aun así no recuperan positivos. Un mínimo absoluto, una capacidad máxima o una condición por grupos son extensiones posibles, pero deben definirse antes de mirar el resultado que se pretende aceptar.

El notebook 06 compara candidatos con remuestreo pareado. Ese análisis ayuda a interpretar variabilidad, pero no modifica silenciosamente la política obligatoria. Un intervalo exploratorio que cruza cero sugiere que la evidencia de mejora es débil bajo sus supuestos; no prueba equivalencia ni impone por sí mismo una regla de despliegue. La decisión técnica debe explicar qué significa aceptar no inferioridad y qué costos hacen razonable cambiar.

## El punto de corte de una transición

El registro local reemplaza un archivo temporal por `current.json`. Esa operación reduce el riesgo de que un lector observe JSON escrito a medias. Sin embargo, después añade una línea a `audit.jsonl` en otra operación. Si el proceso falla entre ambas, puede quedar un puntero actualizado sin la línea correspondiente. Es incorrecto llamar a esas dos escrituras una transacción atómica completa.

También existe una carrera si dos operadores comparan contra el mismo vigente y promueven casi simultáneamente. El segundo puede sobrescribir una decisión que no evaluó. Para múltiples escritores se requiere bloqueo, control de versión esperado o un registro transaccional. El caso docente limita explícitamente la operación a un escritor; conocer la frontera es parte de aprender a escalar el diseño.

La API carga el modelo al inicio. Cambiar un archivo no altera el objeto que ya vive en memoria. Por eso la condición final se observa por HTTP, no solo leyendo el disco. En Compose, además, el registro del contenedor está en un volumen diferente del directorio local. Es posible tener dos punteros correctos y dos versiones distintas porque se está consultando otro entorno.

### Protocolo de promoción verificable

1. Registrar versión servida y verificar que corresponde al vigente esperado.
2. Cargar y verificar integridad del candidato; comparar ambos sobre la validación acordada.
3. Revisar elegibilidad, efectos por grupos, compatibilidad y presupuesto operativo.
4. Registrar actor, motivo y evidencia; cambiar el puntero con un único operador.
5. Reiniciar la instancia correcta y esperar readiness con un tiempo límite.
6. Consultar metadatos y realizar una predicción válida, conservando versión y respuesta.
7. Observar servicio y decidir cierre o reversión según condiciones declaradas.

No basta con que cada comando retorne código cero. La comparación pudo ejecutarse en local mientras la consulta HTTP apunta al contenedor. La evidencia debe vincular host, puerto, registro y versión para que el recorrido sea consistente.

## Rollback y compatibilidad hacia atrás

Rollback recupera una versión anterior del sistema o de sus componentes. En este laboratorio cambia la referencia del modelo; no revierte automáticamente una migración de base de datos, una nueva dependencia ni un contrato incompatible de API. Una versión antigua puede existir y ser incapaz de arrancar en el entorno nuevo. Por eso conservar el archivo no garantiza recuperabilidad.

Antes de una actualización se debe conocer qué componente se revertirá y con qué entorno. La imagen de contenedor ayuda a preservar dependencias, pero los volúmenes y fuentes externas siguen fuera de ella. Si un candidato exigiera una feature nueva no disponible para el modelo anterior, el plan de recuperación tendría que conservar o reconstruir la transformación apropiada. Las compatibilidades deben probarse, no deducirse únicamente del nombre de versión.

La función local de rollback usa `previous`. Después de revertir, el nuevo registro señala como anterior a la versión de la que se salió. Invocarla de nuevo puede alternar entre las dos; no representa una navegación arbitraria por toda la historia. Para recuperar una versión específica de hace varias actualizaciones se necesitaría una operación explícita y una política distinta. El ejercicio exige un único ensayo claramente documentado.

## Comparar estrategias de despliegue

| Estrategia | Cómo cambia el tráfico | Evidencia imprescindible | Costo o límite |
|---|---|---|---|
| Sustitución con reinicio | Una instancia cambia de modelo | Readiness, versión y smoke test | Puede interrumpir servicio |
| Blue-green | Conmutación entre dos entornos | Paridad de configuración y salud del nuevo | Capacidad duplicada durante transición |
| Canary | Fracción creciente recibe candidato | Métricas por versión y asignación comparable | Requiere suficiente tráfico y reglas de parada |
| Shadow | Candidato calcula sin decidir | Correspondencia entre entradas y resultados | Costo extra; no mide todos los efectos de actuar |

Un canary del 5 % con veinte solicitudes ofrece aproximadamente un caso esperado; no tiene volumen para evaluar equidad o calidad con etiquetas tardías. Las señales rápidas serán errores, latencia y contratos. La confirmación predictiva puede requerir mucho más tiempo. Si la asignación de tráfico no es comparable, una diferencia de métricas puede deberse al segmento asignado y no al modelo.

Shadow evita que el candidato tome la acción principal, pero sus resultados contrafactuales siguen sin observarse si una decisión distinta habría cambiado la respuesta real. Además, puede afectar indirectamente al sistema al consumir CPU o servicios externos. «Sin impacto en decisiones» no significa «sin costo ni riesgo operativo». El material explica estas estrategias, pero solo implementa sustitución y reinicio en el laboratorio obligatorio.

## Tabla de fallos para ensayar

| Falla | Resultado deseado | Evidencia de protección |
|---|---|---|
| Candidato no elegible | Conservar vigente | Puntero y versión HTTP sin cambios |
| Artefacto alterado | Rechazar carga | Error de integridad sin promoción |
| Versión ya existente | Evitar sobrescritura | Artefactos anteriores conservados |
| Reinicio sin modelo válido | Readiness 503 | Proceso vivo, servicio retirado o no usado |
| Modelo correcto en disco, antiguo en API | Detectar divergencia | Metadatos HTTP diferentes del puntero |
| Ausencia de antecesor | Rechazar rollback | Mensaje explícito, sin inventar versión |

Estos escenarios deben ejecutarse en un directorio de prueba o un entorno de laboratorio controlado. No se alteran artefactos propios de una entrega válida para fabricar evidencia. Las pruebas automatizadas usan temporales y el equipo conserva los resultados necesarios para explicar por qué el fallo fue detectado.

```{admonition} Caso de revisión
:class: dropdown
El puntero dice candidate-v2, la API devuelve baseline-v1 y `/ready` responde 200. ¿Hubo promoción completa? No. El proceso está listo con un modelo, pero no con la versión esperada. Reiniciar la instancia correcta y comprobar respuesta forma parte de la transición. Un monitor que solo observe readiness no detectará esa discrepancia semántica.
```

La prueba final de recuperación incluye una predicción válida posterior al rollback. Una captura de `current.json` aporta evidencia de configuración; la respuesta HTTP aporta evidencia de ejecución. Mantener ambas evita confundir intención con estado real del servicio.
