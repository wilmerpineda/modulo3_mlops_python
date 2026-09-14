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
