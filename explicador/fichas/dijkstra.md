# Dijkstra
- Expande siempre el nodo con menor costo acumulado g(n), usando una cola de prioridad.
- Óptimo si todos los pesos son no negativos. No usa heurística.
- Complejidad: O((V+E) log V) con montículo.
- Error común: usarlo con pesos negativos (falla).
