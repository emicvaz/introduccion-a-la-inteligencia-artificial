# Reporte: Análisis de Selección de k en Agrupamiento K-Means

[Notebook Original](https://drive.google.com/file/d/1gLRjdWuQ37SUt05gTpm_2-tRm7S4AAn8/view?usp=sharing) y [Notebook Modificado](https://drive.google.com/file/d/1mt6Jp2WjG566J6D4uxOz0JSk6VZnJUsN/view?usp=sharing)

## Preferencia del codo por k=4 en los datos originales de Géron
* Los datos originales colocan tres de los cinco centros alineados en x=−2.8 (con y=1.3, 1.8 y 2.8).
* Aunque su dispersión es pequeña (σ=0.1), la cercanía geométrica hace que los tres grupos se comporten ante la inercia como una única estructura alargada.  Pasar de k=3 a k=4 reduce la inercia de 653.22 a 261.80 (una disminución de 391.42 unidades).
* En contraste, pasar de k=4 a k=5 solo reduce la inercia de 261.80 a 224.07 (una ganancia marginal de apenas 37.73 unidades).  

* Dado que el error cuadrático disminuye de forma insignificante al separar esa columna izquierda, la curva de inercia estabiliza su pendiente y sitúa el codo en k=4.  

## Coincidencia de codo y silueta en k=5 con los blobs separados
* Al redistribuir los cinco centros hacia los cuadrantes lejanos y el origen ([−4,3], [3.5,3], [0,0], [−3.5,−3], [3.5,−3]), los cúmulos quedan aislados espacialmente. En este nuevo escenario, pasar de k=4 a k=5 provoca un desplome drástico de la inercia de 4,794.84 a 509.70, eliminando 4,285.14 unidades de error.  

* De k=5 a k=6, la inercia únicamente desciende 28.19 unidades (de 509.70 a 481.51), marcando un codo incuestionable en k=5.  

* De forma complementaria, el coeficiente de silueta alcanza su valor máximo global en k=5 con un registro de 0.8617, superando a k=4 (0.7209) y a k=6 (0.7449).  

## Ajustes requeridos si el codo persistiera en k=4
* Si el codo se mantuviera en k=4, indicaría que la distancia entre centros aún no supera el umbral de separabilidad
* Frente a esto, se debe incrementar la distancia euclidiana entre los centroides en conflicto para erradicar cualquier frontera que se comparta entre grupos.

* Asimismo, se debe disminuir el parámetro blob_std para encoger el radio de las nubes gaussianas y evitar el traslape en las distribuciones