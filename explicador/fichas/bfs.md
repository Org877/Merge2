# BFS (búsqueda en anchura)
- Usa una cola (FIFO) y explora por niveles: primero todos los vecinos a 1 salto, luego a 2, etc.
- Garantiza el camino con MENOS ARISTAS (no necesariamente el de menor costo si hay pesos).
- Complejidad: O(V+E) en tiempo, O(V) en espacio.
- Error común: asumir que es óptimo en grafos ponderados.
