# Testing automatizado de datos, modelos y pipelines

## Una pirámide de riesgos

Probar funciones pequeñas localiza fallos; probar integración confirma conexiones; un smoke test valida que la imagen inicia. Las tres capas aportan evidencia distinta. Una prueba que repite exactamente la implementación suele confirmar poco; una prueba útil fuerza un caso que antes podría pasar inadvertido.

| Capa | Caso | Resultado esperado |
|---|---|---|
| Datos | Checksum alterado | Rechazo explícito |
| Contrato | Falta columna o campaign negativo | Lote rechazado |
| Features | Aparece duration | Excluida del entrenamiento y rechazada en API |
| Evaluación | Ventana de una sola clase | AUC no definida |
| Etiquetas | Identificador repetido | Error, sin doble conteo |
| API | Sin modelo | Health 200, readiness 503 |
| Ciclo | Candidato peor | No cambia versión vigente |
| Recuperación | Revertir | Vuelve versión previa y se verifica servicio |

```python
def test_fuga():
    from bank_ops.config import FEATURES
    assert "duration" not in FEATURES
    assert "y" not in FEATURES
```

Esta prueba protege una decisión de disponibilidad temporal, pero no detecta una transformación que use filas futuras. Por ello también se revisan particiones, encoders y fit exclusivamente en entrenamiento.

## Determinismo y costo
Semillas y snapshot reducen variabilidad. No exigir una métrica idéntica al último decimal en plataformas distintas: probar propiedades, rangos y tolerancias justificadas. Separar pruebas rápidas del entrenamiento grande. El conjunto docente es pequeño y permite una integración real; un proyecto industrial necesitaría suites con presupuestos de tiempo.

## Pruebas de pipeline
Una falla intermedia debe detener la promoción. Simular candidato deteriorado, artefacto alterado y versión ya existente. La suite de referencia realiza entrenamiento real en directorios temporales, para no modificar el registro del usuario. El candidato corrupto usado por el test no representa una versión válida de producción.

**Práctica:** añada una prueba de categoría nueva y otra de lote sin positivos. Explique cuál evalúa robustez de inferencia y cuál honestidad de evaluación.

<!-- MANUAL AVANZADO -->

## Diseñar pruebas desde fallos plausibles

Una suite útil comienza por un inventario de riesgos: datos incompatibles, fuga de información, probabilidades inválidas, artefactos alterados, promociones incorrectas y servicio no preparado. Cada riesgo se traduce en una propiedad observable y una prueba con una expectativa independiente del detalle de implementación. Probar que una función devuelve exactamente el mismo diccionario que acabamos de construir dentro de la prueba puede no proteger ninguna de esas propiedades.

La API puede responder correctamente a una solicitud válida y fallar ante una categoría nueva; un gate puede aceptar un candidato bueno y aceptar también uno peor por un signo invertido. Por eso la cobertura de escenarios positivos necesita acompañarse de fallos controlados y casos de frontera. El número de tests o el porcentaje de líneas ejecutadas no demuestra por sí solo que se hayan evaluado esas decisiones.

Las pruebas del starter incluyen una omisión deliberada para A3-02. La ampliación del libro enseña cómo razonar sobre el ensayo, pero no completa la solución evaluada. El equipo debe implementar la prueba de transición y justificar su evidencia. Mantener esa frontera permite que el manual sea profundo sin convertirse en una entrega resuelta para copiar.

## Capas de prueba y evidencia diferente

Una prueba unitaria puede verificar cómo se calcula cobertura con dos identificadores. Una de integración comprueba que un modelo entrenado se guarda y vuelve a cargar con su manifiesto. Una prueba HTTP comprueba contrato y estados del servicio. Un smoke test del contenedor verifica que la imagen inicia en el entorno esperado. Ninguna capa reemplaza automáticamente a las demás.

En ML hay además propiedades estadísticas. Una prueba puede exigir que un modelo supere un mínimo en un conjunto controlado, pero ese mínimo debe ser estable y tener sentido. Un test que falla por una diferencia de 0.000001 entre plataformas puede consumir atención sin detectar deterioro real. A la inversa, una tolerancia enorme puede permitir un error serio. Los rangos deben derivarse del riesgo y del experimento, no ajustarse después de cada fallo para conservar el color verde.

La suite rápida debería detectar errores de contrato sin entrenar repetidamente el bosque completo. Las pruebas de ciclo requieren algunos artefactos reales porque cargar, comparar y servir implica conexiones que un mock no reproduce. Separar presupuestos de ejecución permite mantener retroalimentación rápida y reservar ensayos costosos para cambios relevantes o ejecución programada.

## Fixtures, aislamiento y efectos secundarios

Una fixture prepara condiciones repetibles y puede limpiar recursos después. En el proyecto, `tmp_path` ofrece un directorio temporal y `monkeypatch` redirige constantes de artefactos y reportes de los módulos que las importaron. Cambiar solo la variable original en config no necesariamente cambia referencias ya importadas con `from ... import ...`; hay que conocer dónde se consulta el valor. [Fixtures en pytest](https://docs.pytest.org/en/stable/how-to/fixtures.html).

El aislamiento evita que una prueba dependa del modelo que el estudiante dejó activo ayer. También impide que un ensayo de corrupción altere la versión válida de su laboratorio. La prueba debe crear sus propios recursos, modificar únicamente esos recursos y verificar el resultado. Si solo pasa en cierto orden, probablemente existe estado compartido o una dependencia no declarada.

```python
# Ejemplo autónomo: guardar como prueba adicional de estudio fuera de la entrega.
import pandas as pd
import pytest
from bank_ops.monitor import delayed_performance

def test_probabilidad_fuera_de_rango():
    predictions = pd.DataFrame({
        "prediction_id": ["demo-1"],
        "probability": [1.2],
        "model_version": ["demo"]
    })
    labels = pd.DataFrame({"prediction_id": ["demo-1"], "target": [1]})
    with pytest.raises(ValueError, match="Probabilidad inválida"):
        delayed_performance(predictions, labels)
```

La entrada viola una propiedad del dominio sin depender de un modelo entrenado. El mensaje ayuda a identificar la frontera esperada. Esta prueba no demuestra que todas las probabilidades futuras serán calibradas: rango válido y calibración son propiedades diferentes. Ese tipo de delimitación debe acompañar la lectura de toda prueba.

## Contratos de datos y semántica

La parametrización del starter introduce columna faltante, nulo, target inválido, campaign negativo y lote vacío. Cada perturbación representa una clase de fallo. No conviene introducir varios errores al mismo tiempo en una prueba unitaria de contrato: el primer rechazo puede ocultar que los demás no se detectan. Los ensayos compuestos pertenecen a otra capa, donde se estudia el comportamiento del pipeline completo.

La exclusión de duration protege disponibilidad temporal, pero no basta con comprobar su ausencia literal en FEATURES. Una transformación podría usarla indirectamente o ajustar estadísticas con validation. Por eso se revisa el procedimiento de fit, la construcción de particiones y el origen de cada feature. La fuga puede existir sin una columna cuyo nombre parezca sospechoso.

Un checksum alterado se prueba modificando bytes de un artefacto temporal, no cambiando la huella esperada para que vuelva a pasar. El test verifica que la lectura rechaza contenido distinto del manifiesto. No prueba autenticidad de la fuente del manifiesto, como se discutió en trazabilidad. Nombrar correctamente la propiedad evita sobreestimar la protección.

## Fronteras numéricas del gate

Los límites de tolerancia deben probarse justo dentro, exactamente sobre y justo fuera de la frontera. Para una caída permitida de 0.005, una comparación con 0.0049, 0.0050 y 0.0051 de deterioro revela errores de signo o desigualdad. La representación de punto flotante requiere valores y aserciones adecuados; no se debe utilizar una tolerancia de test que borre deliberadamente la frontera que se está comprobando.

El gate también necesita casos de AP indefinida, metadatos incompatibles y candidato que mejora una métrica mientras incumple otra. Una prueba que solo compara un modelo consigo mismo cubre equivalencia, pero no demuestra rechazo. La actividad pide una réplica para ensayar transición y un candidato deteriorado para probar la protección; sus propósitos son distintos.

Si compare recalcula métricas a partir de artefactos reales, algunos tests pueden sustituir componentes para estudiar exclusivamente la lógica de política, mientras otros deben recorrer carga y evaluación real. Los mocks ayudan a aislar ramas, pero si toda la suite sustituye el estimador nunca detectará un error de columnas en `predict_proba`. La mezcla de capas es deliberada.

## API: contrato, estado y ciclo de vida

El contexto `with TestClient(api.create_app())` ejecuta el ciclo de vida de la aplicación. Esto importa porque el modelo se carga al inicio, no al importar el módulo. Una prueba que omite startup puede observar un estado diferente del servicio real. Las aserciones deben distinguir 200 en health, 503 en readiness sin modelo y 422 para payload inválido.

La recuperación no se prueba solo llamando rollback. Debe construirse una nueva instancia o reiniciarse el proceso que carga el artefacto, consultar la versión y enviar una entrada válida. Si se reutiliza una app ya iniciada, puede conservar el modelo anterior en memoria. Ese comportamiento no es necesariamente un bug: corresponde al contrato de carga única del ejemplo.

Las métricas se registran por aplicación para evitar colisiones en tests. Una prueba de instrumentación puede enviar solicitudes y comprobar que existen series con etiquetas normalizadas. No debería exigir tiempos exactos, porque dependen de planificación y máquina. Para latencia se prueban unidades, positividad y presencia de observaciones; el cumplimiento de SLO se estudia con un ensayo de carga separado.

## Reproducibilidad y pruebas inestables

Una prueba inestable puede revelar dependencia de red, orden, reloj o recursos compartidos. Reintentar hasta que pase oculta el problema y reduce confianza en la suite. Primero se identifica la fuente: dataset descargado durante test, puerto ocupado, nombre de versión fijo, semilla no controlada o expectativa demasiado estricta. Después se corrige el diseño, conservando reintentos solo donde exista una condición transitoria entendida.

El proyecto evita descargar datos durante pruebas y usa temporales para artefactos. Las dependencias de instalación siguen requiriendo red en una máquina nueva. Un fallo al instalar no debe convertirse en un test estadístico fallido ni corregirse modificando tolerancias de AP. La clasificación del fallo determina el responsable y la acción siguiente.

## Matriz de pruebas para revisar una entrega

| Pregunta | Evidencia mínima | Evidencia insuficiente |
|---|---|---|
| ¿Se rechaza calidad inválida? | Fallos aislados por contrato | Solo ejecutar un lote válido |
| ¿Se protege evaluación? | Particiones y fit revisados | Semilla fija sin revisar datos |
| ¿Se bloquea deterioro? | Candidato que incumple y vigente intacto | Comparar dos réplicas iguales |
| ¿Se recupera servicio? | Versión y predicción después de reinicio | Leer únicamente el puntero |
| ¿CI ejecuta lo exigido? | Log de pytest y fallo reparado | Compileall o checks omitidos |

```{admonition} Taller opcional
:class: dropdown
Proponga un cambio de código que una suite ingenua no detectaría: invertir una desigualdad, usar test para escoger umbral o omitir reinicio. Para cada cambio, escriba la propiedad que debe fallar y la capa adecuada. No es necesario modificar la entrega final para introducir todos esos defectos; el objetivo es aprender a evaluar la capacidad de detección de una prueba.
```

La suite debe servir como evidencia revisable de riesgos controlados. Una buena explicación de sus límites aumenta su valor: permite saber qué seguir comprobando en el laboratorio, en observabilidad y en revisión humana.
