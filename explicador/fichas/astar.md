# A*
- Prioridad f(n) = g(n) + h(n): costo real acumulado más estimación al destino.
- Es óptimo si h es admisible (nunca sobreestima el costo real). Con h=0 se comporta como Dijkstra.
- Suele visitar menos nodos que Dijkstra cuando la heurística es buena.
- Error común: usar una heurística que sobreestima, lo que puede dar rutas no óptimas.
