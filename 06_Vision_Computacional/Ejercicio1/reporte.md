# Reporte de Práctica: Detección de Objetos con YOLOv8
## 1. ¿Qué clases detectó YOLO en las fotos de Ultralytics y cuáles en la tuya?
* Imágenes de muestra originales (Ultralytics):
zidane.jpg: Se detectaron 2 personas (person) y 1 corbata (tie). Y de
bus.jpg: Se identificaron 4 personas (person), 1 autobús (bus) y 1 señal de alto (stop sign).
* Imagen personalizada (mi_foto.jpg):
Sobre la fotografía seleccionada del espacio de trabajo/reunión, el modelo identificó con éxito instancias de person (2), laptop (1) y cell phone (1).
## 2. ¿Algún objeto evidente de tu foto no salió etiquetado? ¿Por qué podría pasar (clase que no está en COCO, objeto chico, recorte, umbral de confianza)?
* Fuera del dataset COCO: Elementos evidentes en la mesa como cuadernos de notas y bolígrafos no fueron detectados porque no existen dentro de las 80 clases predefinidas de COCO.
* Umbral de confianza y escala: Objetos como tazas o sillas en los bordes quedaron por debajo del umbral mínimo de confianza (conf=0.25) o se descartaron por oclusión/ángulo para el tamaño reducido del modelo nano (yolov8n.pt).
## 3. Comparación entre la predicción CLI (!yolo predict) y la API de Python (model(...))
* Ambas ejecuciones arrojaron resultados consistentes en la localización de los objetos principales (person, laptop, cell phone). Las 3 épocas de reentrenamiento con coco128.yaml son muy breves para alterar significativamente las detecciones, manteniendo las mismas etiquetas con variaciones mínimas de confianza decimal.