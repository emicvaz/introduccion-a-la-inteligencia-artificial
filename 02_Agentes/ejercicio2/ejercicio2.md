# Descripción PEAS para 8 agentes


### 1. Asistente virtual de voz
- **Performance:**  Alta precisión en la respuesta de los comandos de voz con cohesión bien establecida de acuerdo a lo formulado por el humano
- **Environment:**  Espacios físicos con con silencio o ruido ambiental. Espacios físicos con silencio o ruido ambiental. (Parcialmente observable, estocástico, secuencial, dinámico, continuo, multiagente).
- **Actuators:**  Altavoz, pantalla y disparadores de comandos API
- **Sensors:** Micrfónos

### 2. Robot aspirador doméstico 

- **Performance:** Porcentaje del suelo limpiado
- **Environment:** Suelo de una habitación o casa con alfombras, pisos duros, muebles, obstáculos y suciedad (Completamente observable observable, estocástico, secuencial, dinámico, continuo, monoagente/multiagente según si hay personas o mascotas).
- **Actuators:** El avance de las ruedas, usar los cepillitos o el trapeador
- **Sensors:** Sensor de impacto, sensor de suciedad o sensor de batería


### 3. Sistema de recomendación de streaming
- **Performance:** Aceptación de los usuarios a las recomendaciones
- **Environment:** Plataforma de Streaming, (Parcialmente observable, estocástico, secuencial, dinámico/semidinámico, discreto, multiagente).
- **Actuators:** Sacar los títulos dentro del render de recomendaciones que recomienda el sistema (online) o notificaciones periodicas de los títulos recomendados (offline)
- **Sensors:** Datos exclusivamente del historial del usuario, así como datos de la telemetría del usuario

### 4. Vehículo autónomo en ciudad 

- **Performance:**  Métricas de seguridad vial, cumplimiento de leyes de tránsito, minimización del tiempo de viaje
- **Environment:** Calles urbanas, peatones, ciclistas, otros vehículos, señales de tráfico, semáforos, obstáculos y condiciones climáticas variables.(Parcialmente observable, estocástico, secuencial, dinámico, continuo, multiagente).
- **Actuators:** Control de dirección, acelerador, sistema de frenos, luces direccionales/faros, claxon y pantalla/audio para pasajeros.
- **Sensors:** Cámaras de video, sensores de proximidad, receptor GPS, sensores de velocidad de ruedas

### 5. Agente de trading algorítmico en bolsa

- **Performance:**  Maximizar el retorno sobre la inversión
- **Environment:** Mercados financieros electrónicos (bolsas de valores como NYSE, NASDAQ, BMV), libros de órdenes en tiempo real, otros operadores.(Parcialmente observable, estocástico, secuencial, dinámico, continuo en tiempo/precios, multiagente competitivo).
- **Actuators:**  Emisión, modificación y cancelación de órdenes de compra/venta, llamadas a la API de ejecución del broker.
- **Sensors:**  Feeds de datos de mercado en tiempo real, confirmaciones de ejecución de órdenes, saldo de cuenta disponible.

## 6. Sistema de diagnóstico médico asistido por IA

- **Performance:** Presición en los diagnósticos
- **Environment:** Registros clínicos del paciente. (Parcialmente observable, estocástico, episódico o secuencial según el tipo de diagnóstico, estático, monoagente).
- **Actuators:** Reportes de diagnóstico
- **Sensors:** Imágeens médicas, datos de laboratorio, texto clínico en formato libre (descripciones y consultas).


### 7. Dron de inspección de infresctructura

- **Performance:**  Alta precisión en la detección y clasificación de fallas
- **Environment:**  Estructuras físicas (puentes, edificios, etc.).(Parcialmente observable, estocástico, secuencial, dinámico, continuo, monoagente).
- **Actuators:**  Señal de transmisión de telemetría al usuario que controla el dron.
- **Sensors:** Cámaras visuales de alta resolución, cámaras termográficas/infrarrojas, móduclo con GPS, barómetro.

### 8. Agente jugador de ajedrez

- **Performance:** Cumplimiento de las reglas en sus movimientos
- **Environment:**  Tablero de ajedrez con sus dimensiones, piezas de ajedrez, reloj de ajedrez, jugador rival.(Completamente observable, determinista, secuencial, estático mientras piensa su jugada/semidinámico con reloj, discreto, monoagente).
- **Actuators:**  Son dos actuadores consecutivos, el movimiento del oponente y el reloj en marcha del agente
- **Sensors:** Módulo de lectura de las piezas en posición propia y la del rival, reloj con el que se desarrolla ej juago.