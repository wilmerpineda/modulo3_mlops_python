# Caso de estudio: Bank Marketing

## Pregunta y momento de predicción

¿Cuál es la probabilidad de que una persona suscriba un depósito? En el laboratorio se predice antes de conocer el resultado del contacto. El target `y` vale `yes` o `no`. Una probabilidad no representa una garantía ni una recomendación individual.

Se utiliza la variante `bank-full.csv`, de 45 211 registros. La fuente publica información histórica de campañas de una entidad portuguesa. Consulte [UCI y su documentación](https://archive.ics.uci.edu/dataset/222/bank+marketing). La copia entregada incluye un manifiesto de procedencia y checksum. Si procede de una copia local normalizada, el manifiesto distingue ese hecho de una descarga verificada.

## Variables y fuga de información

`duration` se conoce al finalizar la llamada y se excluye. `age` se reserva para auditoría, no para entrenamiento. También se excluye `day`, para reducir dependencias de calendario mal especificadas. Se usan balance, número de contactos, historial y atributos categóricos conocidos al momento definido. `campaign` se interpreta como contador disponible al iniciar el intento actual: si el proceso real solo lo conoce al cierre, habría que desplazarlo o eliminarlo.

Eliminar edad no elimina sus proxies: ocupación, estado civil e historia crediticia pueden correlacionarse con ella. La auditoría sigue siendo necesaria.

## Particiones y límites

Mantener el orden original y dividir 60 % para entrenamiento, 20 % para validación y 20 % para prueba. Ajustar escalado, one-hot y clasificador solo con entrenamiento. Usar validación para comparar candidatos; reservar prueba para el informe final después de fijar decisiones.

El archivo no contiene fecha completa ni identificador individual. El orden no permite reconstruir una cronología exacta ni garantizar que una persona no aparezca en varias particiones. No inventar años a partir del mes. Registrar estas limitaciones en la model card.

## Hipótesis experimental

El baseline es una regresión logística. Un bosque aleatorio será un candidato, pero no se presupone que lo supere. Se crean controles de validación para observar estabilidad y cambios artificiales. La inversión de etiquetas es una intervención extrema de enseñanza, no una afirmación sobre concept drift real en UCI.

## Artefactos

`data/provenance.json` identifica el snapshot; cada carpeta de versión contiene modelo y metadatos; `current.json` apunta a la versión seleccionada; los reportes conservan resultados. Las huellas detectan cambios accidentales: no sustituyen firmas criptográficas ni controles de acceso.
