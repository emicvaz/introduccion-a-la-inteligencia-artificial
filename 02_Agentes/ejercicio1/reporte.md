# Análisis de Rendimiento de los Agentes
## ¿Qué agentes lograron salir con el oro en tu mapa y cuáles no?

* **02_simple_reflex_agent.py**: Falló. No logró recolectar el oro ni salir de la cueva, agotando el límite de pasos *(steps=200, score=-200.0)*. <br>

* **03_model_based_agent.py**: Éxito. Recolectó el oro y escapó con puntaje positivo *(steps=17, score=983.0)*. <br>

* **04_goal_based_agent.py**: Éxito. Planificó y ejecutó la secuencia óptima hacia la meta *(steps=17, score=983.0)*.

* **05_utility_based_agent.py**: Éxito. Maximizó la recompensa explorando casillas seguras *(steps=33, score=967.0)*. <br>

* **06_learning_agent.py**: Éxito. Tras 1,500 episodios de entrenamiento, la política codiciosa halló **la ruta más corta** *(steps=12, score=988.0)*. <br>
## Preguntas de Reflexión

### ¿Por qué el agente de reflejo simple falla (o tiene suerte) en tu diseño?

El agente de reflejo simple carece de memoria histórica. Al avanzar hacia la casilla [3, 1], percibe el Stench producido por el Wumpus ubicado en [4, 1]. Su tabla de reglas le dicta girar y retroceder a casillas seguras como [2, 1], donde la percepción de peligro desaparece, provocando que vuelva a orientarse y avanzar hacia adelante. Al no poder recordar casillas visitadas ni construir un mapa del entorno, entra en un loop infinito de *der,abj,izq,arr*. <br>

### ¿Cómo cambia el resultado del agente basado en modelo si acercas o alejas un pit de la casilla inicial?
Pit cercano a [1, 1] genera una percepción de brisa inmediata en el turno inicial. Debido a la aversión estricta al riesgo del agente y a la imposibilidad de desambiguar la ubicación exacta del pozo sin casillas de contraste, el agente queda bloqueado sin explorar por la ambiguedad de 50% - 50%.