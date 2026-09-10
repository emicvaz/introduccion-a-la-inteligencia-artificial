# Análisis de la Red Neuronal: Caso Iris bajo Numpy y Keras

## ¿El error bajó al añadir dos capas, o se estancó / empeoró?

Al incorporar dos capas intermedias con la función de activación sigmoide, el rendimiento empeoró significativamente en ambas implementaciones

* En Keras, la red 4X3X3 redujo el error cuadrático medio hasta 0.17016, mientras que la red profunda de 4X3X3X3 prácticamente no aprendió, terminando con un MSE de 0.22217 . Esto se evidencia en la predicción de prueba para [3, 3, 1, 1], donde la red profunda predice para el vector [0.334, 0.333, 0.334], lo que indica que las neuronas de salida quedaron completamente saturadas en el valor medio = 1/3, sin capacidad de discriminar entre clases.  

* En NumPy, el fenómeno fue aún más pronunciado: la red 4X3X3 redujo su error progresivamente a lo largo de las 500 épocas, mientras que la red de 4X3X3X3 capas mantuvo una curva de pérdida casi horizontal alrededor de 0.68, evidenciando un estancamiento total desde las primeras iteraciones.

## ¿Las curvas de NumPy y Keras se parecen con la misma topología?

Aunque ambas logran converger en la red original de dos capas, presentan diferencias en la forma y velocidad de descenso debido a detalles de implementación: 

* Propagación y Retroprogagación: La notebook 01 actualiza los pesos de forma estrictamente aleatoria, generando fluctuaciones en los pesos de forma inmediata. Keras, al usar model.fit() sin batch_size especificado, utiliza por defecto un tamaño de lote de 32 (tamaño default), lo que produce una curva de aprendizaje más suave y estable.  

* Inicialización de pesos: NumPy inicializa con una distribución uniforme con media cero (rand - 0.5) con pesos pequeños, mientras que Keras utiliza por defecto la inicialización propia de la paquetería, la cual escala la varianza en función del abanico de entrada y salida, mitigando en parte la saturación temprana.  

* Escala del cálculo de error: En la notebook 01 el error graficado se calcula como la suma de los errores al cuadrado dividido entre len(X) sin normalizar por el número de neuronas de salida, mientras que tf.keras.losses.MeanSquaredError() promedia tanto sobre el lote como sobre las 3 dimensiones de salida, explicando la diferencia en la magnitud absoluta inicial

## Con sigmoides apiladas y MSE, ¿tiene sentido que una red más profunda no aprenda mejor en Iris? Relaciónalo con lo que viste en las gráficas.

* Desvanecimiento del gradiente: La derivada de la función sigmoide es s'(x)=s(x)(1-s(x)), 
cuyo valor máximo teórico es de solo 0.25. En la retropropagación de la red profunda de 4 capas, el error de la capa 1 depende del producto acumulado de las derivadas y pesos de las tres capas posteriores.
Al encadenar 4 capas con sigmoide, los términos multiplicativos <=0.25 amortiguan exponencialmente la señal del gradiente hacia las primeras capas, dejando los pesos iniciales prácticamente inmóviles con una tasa de aprendizaje tan conservadora como 0.03. 

* Simplicidad del problema: Iris es un conjunto de datos linealmente separable para Setosa y separable con fronteras simples para Versicolor y Virginica (como lo vimos en clase). Añadir más capas no solo introduce redundancia de parámetros para 150 muestras, sino que genera cuellos de botella severos en la optimización si no se emplean otro tipo de funciones de activación.
