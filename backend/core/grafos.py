import random
from collections import deque
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
            adj.setdefault(v, [])  # nodos que solo aparecen como destino
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

    heuristica_dada = bool(heuristica)
    if not heuristica:
        heuristica = {k: 0.0 for k in adj.keys()}

    def h(n):
        return float(heuristica.get(n, 0.0))

    traza = []
    
    if algoritmo == "bfs":
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


    elif algoritmo == "hill":  # Hill-Climbing (ascenso/descenso de colina por la heurística)
        if not heuristica_dada:
            raise ValueError("Hill-Climbing necesita una heurística h(n) (por ejemplo A:3, B:2, D:0).")
        rng = random.Random(7)
        mejor = None
        intentos = max(0, reinicios) + 1
        orden_visita = []
        for intento in range(intentos):
            actual, camino, costo = origen, [origen], 0.0
            orden_visita.append(origen)
            traza.append({"paso": len(orden_visita), "descripcion": f"Intento {intento + 1}: inicia en {origen} (h={h(origen)})", "nodo": origen})
            visitados_loc = {origen}
            atascado = False
            primer_paso = intento > 0  # los reinicios arrancan con un primer movimiento aleatorio
            while actual != destino:
                vecinos = [(v, p) for v, p in adj.get(actual, []) if v not in visitados_loc]
                if not vecinos:
                    atascado = True
                    break
                if primer_paso:
                    v, p = rng.choice(vecinos)
                    primer_paso = False
                else:
                    v, p = min(vecinos, key=lambda x: h(x[0]))
                    if h(v) >= h(actual) and v != destino:
                        atascado = True
                        traza.append({"paso": len(orden_visita) + 1, "descripcion": f"Mínimo local en {actual}: ningún vecino mejora h={h(actual)}", "nodo": actual})
                        break
                visitados_loc.add(v)
                camino.append(v)
                costo += p
                actual = v
                orden_visita.append(v)
                traza.append({"paso": len(orden_visita), "descripcion": f"Hill-Climbing avanza a {v} (h={h(v)})", "nodo": v})
            if actual == destino:
                if mejor is None or costo < mejor[1]:
                    mejor = (camino, costo)
                break
            traza.append({"paso": len(orden_visita), "descripcion": f"Intento {intento + 1} atascado en {actual}", "nodo": actual})
        camino_final, costo_total = (mejor if mejor else ([], -1.0))
        return {"camino": camino_final, "costo": costo_total, "orden_visita": orden_visita,
                "nodos_visitados": len(orden_visita), "traza": traza, "atascado": mejor is None}

    else:
        raise ValueError(f"Algoritmo '{algoritmo}' no soportado.")

def alcance_maximo(grafo_raw, origen, dirigido):
    """BFS completo: todos los nodos alcanzables desde el origen con su distancia en saltos."""
    origen = str(origen)
    adj = procesar_grafo(grafo_raw, dirigido)
    if origen not in adj:
        raise ValueError("El nodo de origen no existe en el grafo.")
    dist = {origen: 0}
    cola = deque([origen])
    orden = []
    traza = []
    while cola:
        u = cola.popleft()
        orden.append(u)
        traza.append({"paso": len(orden), "descripcion": f"Visita {u} a {dist[u]} salto(s) del origen", "nodo": u})
        for v, _ in adj.get(u, []):
            if v not in dist:
                dist[v] = dist[u] + 1
                cola.append(v)
    no_alcanzables = sorted(set(adj) - set(dist))
    return {"alcanzables": dist, "no_alcanzables": no_alcanzables, "orden_visita": orden,
            "nodos_visitados": len(orden), "traza": traza}
