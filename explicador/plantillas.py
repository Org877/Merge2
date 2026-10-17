"""Explicaciones de respaldo (sin LLM). Siempre hay texto, aunque Ollama no esté corriendo."""

TEORIA = {
    "afd": "Un AFD (autómata finito determinista) tiene exactamente una transición por estado y símbolo; acepta la palabra si, tras leerla completa, termina en un estado de aceptación.",
    "afnd": "Un AFND puede tener varias transiciones para un mismo símbolo; se simula manteniendo el conjunto de estados activos y acepta si algún estado activo final es de aceptación.",
    "afnde": "Un AFND-ε además permite moverse sin leer símbolos; en cada paso se calcula la ε-clausura (todo lo alcanzable por transiciones ε).",
    "lenguajes": "Un lenguaje es un conjunto de cadenas sobre un alfabeto Σ; sobre ellos se definen unión, intersección, diferencia, concatenación, potencia y clausura de Kleene.",
    "bfs": "BFS recorre por niveles con una cola; garantiza el camino con menos aristas (no necesariamente el de menor costo). Complejidad O(V+E).",
    "dfs": "DFS profundiza por una rama antes de retroceder (pila); encuentra un camino, no necesariamente el más corto. Complejidad O(V+E).",
    "dijkstra": "Dijkstra expande siempre el nodo de menor costo acumulado g(n); es óptimo con pesos no negativos. Complejidad O((V+E) log V).",
    "star": "A* ordena por f(n)=g(n)+h(n); es óptimo si la heurística h es admisible (nunca sobreestima).",
    "greedy": "La búsqueda voraz ordena solo por h(n): es rápida pero no garantiza el camino óptimo.",
    "hill": "Hill-Climbing avanza siempre al vecino con mejor heurística; puede atascarse en un mínimo local, por eso se usan reinicios aleatorios.",
    "alcance": "El alcance máximo se calcula con un recorrido BFS completo: son los nodos con una ruta desde el origen, con su distancia en saltos.",
    "P": "La clase P agrupa problemas resolubles en tiempo polinomial; ordenar es el ejemplo típico.",
    "NP": "En NP una solución se puede VERIFICAR en tiempo polinomial, pero la fuerza bruta para ENCONTRARLA crece de forma exponencial o factorial.",
    "NSPACE": "REACHABILITY está en NL/NSPACE(log n); el teorema de Savitch lo resuelve de forma determinista con O(log² n) de espacio, a costa de más tiempo.",
}


def _camino(c):
    return " → ".join(c) if c else "sin ruta posible"


def generar_plantilla(modulo: str, operacion: str, resultado: dict, metricas: dict | None = None) -> str:
    met = metricas or {}
    t, m = met.get("tiempo_ms", 0), met.get("memoria_kb", 0)
    cierre = f"\n\n**Métricas**: tiempo {t} ms, memoria pico {m} KB (mediciones sobre el cómputo determinista)."

    if modulo == "lenguajes":
        if operacion.startswith("simular_"):
            tipo = operacion.split("_", 1)[1]
            estado = "ACEPTADA" if resultado.get("pertenece") else "RECHAZADA"
            motivo = f" Motivo: {resultado['motivo']}" if resultado.get("motivo") else ""
            pasos = len(resultado.get("traza", [])) - 1
            return (f"**Qué se hizo**: se simuló un {tipo.upper()} sobre la palabra dada.\n\n"
                    f"**Resultado**: la palabra fue **{estado}** tras {max(pasos, 0)} paso(s) de lectura.{motivo}\n\n"
                    f"**Base teórica**: {TEORIA.get(tipo, TEORIA['afd'])}" + cierre)
        if operacion == "analizar_cadena":
            return (f"**Qué se hizo**: se analizó una cadena (longitud, inversa, prefijos, sufijos y conteo de símbolos).\n\n"
                    f"**Resultado**: longitud {resultado.get('longitud')}, inversa `{resultado.get('inversa')}`.\n\n"
                    f"**Base teórica**: {TEORIA['lenguajes']}" + cierre)
        elems = resultado.get("resultado", [])
        return (f"**Qué se hizo**: se aplicó la operación **{operacion}** sobre los lenguajes de entrada.\n\n"
                f"**Resultado**: se obtuvieron {len(elems)} cadena(s): {', '.join(map(repr, elems[:15]))}{'…' if len(elems) > 15 else ''}.\n\n"
                f"**Base teórica**: {TEORIA['lenguajes']}" + cierre)

    if modulo == "rutas":
        if operacion == "alcance_maximo":
            alc = resultado.get("alcanzables", {})
            return (f"**Qué se hizo**: se calculó el alcance máximo desde el nodo de origen.\n\n"
                    f"**Resultado**: {len(alc)} nodo(s) alcanzable(s): {', '.join(f'{k} ({v} saltos)' for k, v in alc.items())}. "
                    f"No alcanzables: {', '.join(resultado.get('no_alcanzables', [])) or 'ninguno'}.\n\n"
                    f"**Base teórica**: {TEORIA['alcance']}" + cierre)
        alg = operacion.replace("buscar_", "")
        if not resultado.get("existe_ruta"):
            extra = " El algoritmo se quedó atascado en un mínimo local." if resultado.get("atascado") else ""
            return (f"**Qué se hizo**: se buscó una ruta con **{alg}**.\n\n**Resultado**: no se encontró ninguna ruta.{extra}\n\n"
                    f"**Base teórica**: {TEORIA.get(alg, '')}" + cierre)
        comp = resultado.get("comparativa", [])
        tabla = ""
        if len(comp) > 1:
            tabla = "\n\n**Comparativa**: " + "; ".join(
                f"{c['algoritmo']} → costo {c['costo']}, {c['nodos_visitados']} nodos" for c in comp)
        return (f"**Qué se hizo**: se buscó una ruta con **{alg}**.\n\n"
                f"**Resultado**: camino `{_camino(resultado['camino'])}` con costo **{resultado['costo']}**; "
                f"se visitaron {resultado['nodos_visitados']} nodos.{tabla}\n\n"
                f"**Base teórica**: {TEORIA.get(alg, '')}" + cierre)

    if modulo == "complejidad":
        filas = []
        for r in resultado.get("comparativa", []):
            estado = " (ABORTADO)" if r.get("abortado") else ""
            filas.append(f"- `{r['algoritmo']}` [{r.get('clase')}, {r.get('complejidad')}]: "
                         f"{r['metricas']['tiempo_ms']} ms, {r['metricas']['memoria_kb']} KB{estado}")
        clases = {r.get("clase") for r in resultado.get("comparativa", [])}
        teoria = " ".join(TEORIA[c] for c in ("P", "NP", "NSPACE") if c in clases)
        avisos = ("\n\n**Avisos**: " + " ".join(resultado.get("avisos", []))) if resultado.get("avisos") else ""
        return ("**Qué se hizo**: se ejecutaron los algoritmos seleccionados sobre el mismo conjunto de datos, de forma secuencial.\n\n"
                "**Resultado**:\n" + "\n".join(filas) + f"\n\n**Base teórica**: {teoria}" + avisos)

    return "Proceso computacional completado con éxito bajo las restricciones del modelo determinista."
