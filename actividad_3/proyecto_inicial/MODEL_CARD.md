# Model card — Bank Marketing

## Uso y límites
Predicción educativa de suscripción a un depósito antes de conocer el resultado de una llamada. No utilizar para decisiones sobre personas reales. Datos históricos portugueses; no representan automáticamente población colombiana ni clientes actuales.

## Datos y transformaciones
UCI Bank Marketing, bank-full.csv, licencia y checksum en data/provenance.json. Particiones ordenadas 60/20/20; el orden ayuda a separar etapas, pero no proporciona fechas completas ni identificación de clientes repetidos. No se puede garantizar independencia por persona.
duration, age y day excluidos. Edad solo para auditoría agregada. Variables como job o marital pueden actuar como proxies. campaign supone disponible el contador de intentos al iniciar el contacto.

## Modelo y evaluación
Regresión logística + escalado + one-hot aprendido solo en entrenamiento. Umbral educativo fijo 0.25, no optimizado con test. AP, ROC AUC, precision, recall, F1, Brier y matriz de confusión. Consultar metadata.json y reports/monitoring.json para resultados calculados.

## Auditoría de equidad
Grupos 18–29, 30–59 y 60–100; n, positivos, negativos, tasa de selección, TPR y FPR. Menos de 30 positivos o negativos: comparación insuficientemente sustentada. No concluir ausencia de discriminación por igualdad de una métrica.

## Operación y responsabilidades
Un operador promueve versiones con responsable y justificación; API reiniciada después de promoción. Reportes y registro local auditables, no resistentes a manipulación. Para producción: almacenamiento inmutable, acceso controlado, evaluación legal y responsables institucionales.

## Completar por el equipo
Versión y commit evaluados; tablas de métricas reales; incidente observado; decisión sobre candidato; limitaciones, medidas de mitigación y fecha de revisión.
