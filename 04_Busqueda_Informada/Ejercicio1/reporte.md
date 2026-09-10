# Reporte de Análisis: Búsqueda Informada (Greedy vs. A*)

## ¿A* encontró el camino de menos km? ¿Greedy coincidió o se desvió?
A* encontró la ruta óptima de menor costo real en distancia con 536 km a través de la ruta: <br> <br>
Timisoara→Arad→Sibiu→Rimnicu Vilcea→Pitesti→Bucharest <br><br>
Greedy Best-First Search se desvió por completo, seleccionando una ruta alternativa significativamente más costosa de 615 km:<br> <br>
Timisoara→Lugoj→Mehadia→Drobeta→Craiova→Pitesti→Bucharest <br> <br>

Como se explica en AIMA, A* evalúa los nodos combinando el costo ya recorrido con el estimado futuro **_f(n)=g(n)+h(n)_**, lo que garantiza encontrar la solución de costo mínimo siempre que la heurística sea admisible (lo es por ser una distancia SLD). Por el contrario, Greedy no ofrece garantías de optimalidad porque ignora el costo acumulado g(n), buscando únicamente minimizar el estimado h(n) al objetivo inmediato.
## ¿Por qué Greedy puede devolver un camino más caro aunque h sea admisible?

La admisibilidad asegura que h(n) nunca sobreestima el costo real restante h(n)≤h∗(n). Sin embargo, el algoritmo Greedy ordena su frontera únicamente bajo el criterio de evaluación f(n)=h(n). Esto lo vuelve vulnerable, ya que prefiere avanzar hacia cualquier nodo que aparentemente está geográficamente más próximo en línea recta al objetivo (por SLD), sin importar cuántos kilómetros de carretera haya acumulado para llegar a él.

En el caso de la ruta elejida, el primer punto de decisión desde Timisoara, los vecinos eran Lugoj (h=244) y Arad (h=366):
* Greedy eligió inmediatamente Lugoj porque 244<366, comprometiéndose con la ruta sur rumbo a Mehadia y Drobeta sin tomar en cuenta costo de sus carreteras. En cambio, 
* A* evaluó f(Lugoj)=g(111)+h(244)=355 y f(Arad)=g(118)+h(366)=484. Aunque inicialmente exploró por el mismo camino, en cuanto los tramos sucesivos fueron incrementando el costo g(n), el valor total de f(n) superó el costo estimado por la ruta hacia el norte, permitiendo a A* rectificar la trayectoria hacia Arad, Sibiu y el desvío óptimo por Rimnicu Vilcea.

## En el camino de A*, ¿f tiende a no disminuir a lo largo de la ruta? Relación con la consistencia de h:

Al seleccionarse Bucharest como destino, el ejercicio utilizó la tabla oficial de distancias en línea recta de AIMA, la cual es una heurística consistente o monótona. La condición de consistencia establece que para cualquier nodo n y sucesor n′ generado por una acción _a_: <br><br>
h(n)≤c(n,a,n)+h(n′) <br><br>
Sumando g(n) a ambos lados, se deduce directamente que f(n)≤f(n), lo cual implica que los valores de f(n) a lo largo de cualquier camino nunca pueden disminuir. <br> <br>
Los datos experimentales obtenidos para la ruta elegida por A* verifican esta propiedad de forma exacta y no decreciente paso a paso: <br><br>
f(Timisoara)=329≤f(Arad)=484≤f(Sibiu)=511≤f(Rimnicu)=531≤f(Pitesti)=535≤f(Bucharest)=536 <br><br>
Como consecuencia fundamental demostrada en AIMA, la consistencia de h(n) garantiza que cuando A* expande un nodo por primera vez, la ruta alcanzada hacia dicho estado es forzosamente la óptima, eliminando la necesidad de reabrir nodos.