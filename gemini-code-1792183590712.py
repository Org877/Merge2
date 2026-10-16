import math
from heapq import heappop, heappush

def procesar_grafo(grafo_dict, dirigido):
    # Normaliza el grafo asegurando simetría si no es dirigido
    adj = {str(k): [] for k in grafo_dict.keys()}
    for u, vecinos in grafo_dict.items():
        u = str(u)
        if u not in adj:
            adj[u] = []
        for vecino in vecinos:
            v, peso = str(vecino[0]), float(vecino[1])
            if (v, peso) not in adj[u]:
                adj[u].append((v, peso))
            if not dirigido:
                if v not in adj:
                    adj[v] = []
                if (u, peso) not in adj[v]:
                    adj[v].append((u, peso))
    return adj

def ejecutar_busqueda_grafo(grafo_raw, origen, destino, dirigido, algoritmo, heuristica=None, reinicios=0):
    origen, destino = str(origen), str(destino)
    adj = procesar_grafo(grafo_raw, dirigido)
    
    if origen not in adj or destino not in adj:
        raise ValueError("El nodo de origen o destino no existen en el grafo.")

    if heuristica is None:
        heuristica = {k: 0.0 for k in adj.keys()}

    def h(n):
        return float(heuristica.get(n, 0.0))

    traza = []
    
    if algoritmo == "bfs":
        from collections import deque
        cola = deque([(origen, [origen], 0.0)])
        visitados = {origen}
        orden_visita = []
        camino_final = []
        costo_total = -1.0

        while cola:
            actual, camino, costo = cola.popleft()
            orden_visita.append(actual)
            traza.append({"paso": len(orden_visita), "descripcion": f"Visita BFS nodo {actual}", "nodo": actual})

            if actual == destino:
                camino_final = camino
                costo_total = costo
                break

            for vecino, peso in adj.get(actual, []):
                if vecino not in visitados:
                    visitados.add(vecino)
                    cola.append((vecino, camino + [vecino], costo + peso))

        return {"camino": camino_final, "costo": costo_total, "orden_visita": orden_visita, "nodos_visitados": len(orden_visita), "traza": traza}

    elif algoritmo == "dfs":
        pila = [(origen, [origen], 0.0)]
        visitados = set()
        orden_visita = []
        camino_final = []
        costo_total = -1.0

        while pila:
            actual, camino, costo = pila.pop()
            if actual in visitados:
                continue
            visitados.add(actual)
            orden_visita.append(actual)
            traza.append({"paso": len(orden_visita), "descripcion": f"Visita DFS nodo {actual}", "nodo": actual})

            if actual == destino:
                camino_final = camino
                costo_total = costo
                break

            for vecino, peso in reversed(adj.get(actual, [])):
                if vecino not in visitados:
                    pila.append((vecino, camino + [vecino], costo + peso))

        return {"camino": camino_final, "costo": costo_total, "orden_visita": orden_visita, "nodos_visitados": len(orden_visita), "traza": traza}

    elif algoritmo == "dijkstra":
        pq = [(0.0, origen, [origen])]
        distancias = {origen: 0.0}
        visitados = set()
        orden_visita = []
        camino_final = []
        costo_total = -1.0

        while pq:
            costo, actual, camino = heappop(pq)
            if actual in visitados:
                continue
            visitados.add(actual)
            orden_visita.append(actual)
            traza.append({"paso": len(orden_visita), "descripcion": f"Dijkstra extrae nodo {actual} con costo {costo}", "nodo": actual})

            if actual == destino:
                camino_final = camino
                costo_total = costo
                break

            for vecino, peso in adj.get(actual, []):
                nuevo_costo = costo + peso
                if vecino not in distancias or nuevo_costo < distancias[vecino]:
                    distancias[vecino] = nuevo_costo
                    heappush(pq, (nuevo_costo, vecino, camino + [vecino]))

        return {"camino": camino_final, "costo": costo_total, "orden_visita": orden_visita, "nodos_visitados": len(orden_visita), "traza": traza}

    elif algoritmo == "star":  # A* (f = g + h)
        pq = [(h(origen), 0.0, origen, [origen])]
        g_costs = {origen: 0.0}
        visitados = set()
        orden_visita = []
        camino_final = []
        costo_total = -1.0

        while pq:
            f, g, actual, camino = heappop(pq)
            if actual in visitados:
                continue
            visitados.add(actual)
            orden_visita.append(actual)
            traza.append({"paso": len(orden_visita), "descripcion": f"A* evalúa nodo {actual} (f={f}, g={g})", "nodo": actual})

            if actual == destino:
                camino_final = camino
                costo_total = g
                break

            for vecino, peso in adj.get(actual, []):
                nuevo_g = g + peso
                if vecino not in g_costs or nuevo_g < g_costs[vecino]:
                    g_costs[vecino] = nuevo_g
                    f_val = nuevo_g + h(vecino)
                    heappush(pq, (f_val, nuevo_g, vecino, camino + [vecino]))

        return {"camino": camino_final, "costo": costo_total, "orden_visita": orden_visita, "nodos_visitados": len(orden_visita), "traza": traza}

    elif algoritmo == "greedy":  # Greedy Best-First Search (f = h)
        pq = [(h(origen), origen, [origen], 0.0)]
        visitados = set()
        orden_visita = []
        camino_final = []
        costo_total = -1.0

        while pq:
            _, actual, camino, costo = heappop(pq)
            if actual in visitados:
                continue
            visitados.add(actual)
            orden_visita.append(actual)
            traza.append({"paso": len(orden_visita), "descripcion": f"Greedy expande nodo {actual} (h={h(actual)})", "nodo": actual})

            if actual == destino:
                camino_final = camino
                costo_total = costo
                break

            for vecino, peso in adj.get(actual, []):
                if vecino not in visitados:
                    heappush(pq, (h(vecino), vecino, camino + [vecino], costo + peso))

        return {"camino": camino_final, "costo": costo_total, "orden_visita": orden_visita, "nodos_visitados": len(orden_visita), "traza": traza}

    else:
        raise ValueError(f"Algoritmo '{algoritmo}' no soportado.")