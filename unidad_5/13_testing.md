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
