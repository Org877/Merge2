"""Explicaciones de respaldo (sin LLM). Siempre hay texto, aunque Ollama no esté corriendo."""

TEORIA = {
    "afd": "Un AFD (autómata finito determinista) tiene exactamente una transición por estado y símbolo; acepta la palabra si, tras leerla completa, termina en un estado de aceptación.",
    "afnd": "Un AFND puede tener varias transiciones para un mismo símbolo; se simula manteniendo el conjunto de estados activos y acepta si algún estado activo final es de aceptación.",
    "afnde": "Un AFND-ε además permite moverse sin leer símbolos; en cada paso se calcula la ε-clausura (todo lo alcanzable por transiciones ε).",
    "regex": "El algoritmo de Thompson transforma una expresión regular en un AFN-ε y la construcción de subconjuntos elimina las transiciones ε para obtener un AFD equivalente que evalúa cadenas en tiempo lineal O(m).",
    "lenguajes": "Un lenguaje es un conjunto de cadenas sobre un alfabeto Σ; sobre ellos se definen unión, intersección, diferencia, concatenación, potencia y clausura de Kleene.",
    "bfs": "BFS recorre por niveles con una cola; garantiza el camino con menos aristas (no necesariamente el de menor costo). Complejidad O(V+E).",
    "dfs": "DFS profundiza por una rama antes de retroceder (pila); encuentra un camino, no necesariamente el más corto. Complejidad O(V+E).",
    "dijkstra": "Dijkstra expande siempre el nodo de menor costo acumulado g(n); es óptimo con pesos no negativos. Complejidad O((V+E) log V).",
    "star": "A* ordena por f(n)=g(n)+h(n); es óptimo si la heurística h es admisible (nunca sobreestima).",
    "greedy": "La búsqueda voraz ordena solo por h(n): es rápida pero no garantiza el camino óptimo.",
    "hill": "Hill-Climbing avanza siempre al vecino con mejor heurística; puede atascarse en un mínimo local, por eso se usan reinicios aleatorios.",
    "alcance": "El alcance máximo se calcula con un recorrido BFS completo: son los nodos con una ruta desde el origen, con su distancia en saltos.",
    "P": "La clase P agrupa problemas resolubles en tiempo polinomial; ordenar o las aproximaciones voraces como TSP Vecino Más Cercano son ejemplos típicos.",
    "NP": "En NP una solución se puede VERIFICAR en tiempo polinomial, pero la fuerza bruta para ENCONTRARLA crece de forma exponencial o factorial.",
    "NSPACE": "REACHABILITY está en NL/NSPACE(log n); el teorema de Savitch lo resuelve de forma determinista con O(log² n) de espacio, a costa de más tiempo.",
    "auditoria_ast": "El análisis estático con el módulo ast inspecciona el árbol sintáctico del código Python sin ejecutarlo: la profundidad de bucles anidados estima el grado polinomial O(n^k) y la recursión ramificada alerta de crecimiento exponencial.",
    "varillas": "En el corte de varillas, la recursión ingenua repite subproblemas y crece en O(2^n). La tabulación bottom-up (programación dinámica) resuelve cada longitud una sola vez en O(n²) y guarda el primer corte óptimo para reconstruir la solución exacta.",
    "probabilistas": "Miller-Rabin (Monte Carlo) mantiene tiempo acotado con una cota de error de falso primo ≤ 4^(-k) tras k rondas. Quicksort Aleatorizado (Las Vegas) siempre entrega el resultado 100% exacto, variando únicamente su tiempo de ejecución con promedio O(n log n).",
}


def _camino(c):
    return " → ".join(c) if c else "sin ruta posible"


def generar_plantilla(modulo: str, operacion: str, resultado: dict, metricas: dict | None = None) -> str:
    met = metricas or {}
    t, m = met.get("tiempo_ms", 0), met.get("memoria_kb", 0)
    cierre = f"\n\n**Métricas**: tiempo {t} ms, memoria pico {m} KB (mediciones sobre el cómputo determinista)."

    if modulo == "lenguajes":
        if operacion == "regex_a_afd":
            afne = resultado.get("resumen_afn_epsilon", {})
            afd = resultado.get("afd", {})
            return (
                f"**Qué se hizo**: se convirtió la expresión regular `{resultado.get('regex')}` a AFN-ε (Thompson, "
                f"{afne.get('num_estados', 0)} estados) y luego a AFD por subconjuntos ({afd.get('num_estados', 0)} estados).\n\n"
                f"**Resultado**: la cadena `{resultado.get('palabra', '')}` fue **{resultado.get('veredicto')}** "
                f"(estado final `{resultado.get('estado_final')}`).\n\n"
                f"**Base teórica**: {TEORIA['regex']}" + cierre
            )
        if operacion.startswith("simular_"):
            tipo = operacion.split("_", 1)[1]
            estado = "ACEPTADA" if resultado.get("pertenece") else "RECHAZADA"
            motivo = f" Motivo: {resultado['motivo']}" if resultado.get("motivo") else ""
            pasos = len(resultado.get("traza", [])) - 1
            return (
                f"**Qué se hizo**: se simuló un {tipo.upper()} sobre la palabra dada.\n\n"
                f"**Resultado**: la palabra fue **{estado}** tras {max(pasos, 0)} paso(s) de lectura.{motivo}\n\n"
                f"**Base teórica**: {TEORIA.get(tipo, TEORIA['afd'])}" + cierre
            )
        if operacion == "analizar_cadena":
            return (
                f"**Qué se hizo**: se analizó una cadena (longitud, inversa, prefijos, sufijos y conteo de símbolos).\n\n"
                f"**Resultado**: longitud {resultado.get('longitud')}, inversa `{resultado.get('inversa')}`.\n\n"
                f"**Base teórica**: {TEORIA['lenguajes']}" + cierre
            )
        elems = resultado.get("resultado", [])
        return (
            f"**Qué se hizo**: se aplicó la operación **{operacion}** sobre los lenguajes de entrada.\n\n"
            f"**Resultado**: se obtuvieron {len(elems)} cadena(s): {', '.join(map(repr, elems[:15]))}{'…' if len(elems) > 15 else ''}.\n\n"
            f"**Base teórica**: {TEORIA['lenguajes']}" + cierre
        )

    if modulo == "rutas":
        if operacion == "alcance_maximo":
            alc = resultado.get("alcanzables", {})
            return (
                f"**Qué se hizo**: se calculó el alcance máximo desde el nodo de origen.\n\n"
                f"**Resultado**: {len(alc)} nodo(s) alcanzable(s): {', '.join(f'{k} ({v} saltos)' for k, v in alc.items())}. "
                f"No alcanzables: {', '.join(resultado.get('no_alcanzables', [])) or 'ninguno'}.\n\n"
                f"**Base teórica**: {TEORIA['alcance']}" + cierre
            )
        alg = operacion.replace("buscar_", "")
        if not resultado.get("existe_ruta"):
            extra = " El algoritmo se quedó atascado en un mínimo local." if resultado.get("atascado") else ""
            return (
                f"**Qué se hizo**: se buscó una ruta con **{alg}**.\n\n**Resultado**: no se encontró ninguna ruta.{extra}\n\n"
                f"**Base teórica**: {TEORIA.get(alg, '')}" + cierre
            )
        comp = resultado.get("comparativa", [])
        tabla = ""
        if len(comp) > 1:
            tabla = "\n\n**Comparativa**: " + "; ".join(
                f"{c['algoritmo']} → costo {c['costo']}, {c['nodos_visitados']} nodos" for c in comp
            )
        return (
            f"**Qué se hizo**: se buscó una ruta con **{alg}**.\n\n"
            f"**Resultado**: camino `{_camino(resultado['camino'])}` con costo **{resultado['costo']}**; "
            f"se visitaron {resultado['nodos_visitados']} nodos.{tabla}\n\n"
            f"**Base teórica**: {TEORIA.get(alg, '')}" + cierre
        )

    if modulo == "complejidad":
        if operacion == "auditar_ast":
            return (
                f"**Qué se hizo**: se auditó el árbol sintáctico (AST) del código Python ({resultado.get('nodos_ast_analizados', 0)} nodos).\n\n"
                f"**Resultado**: profundidad máxima de bucles = **{resultado.get('profundidad_max_bucles', 0)}** "
                f"({resultado.get('total_bucles', 0)} bucle(s) detectado(s), {len(resultado.get('funciones_recursivas', []))} función(es) recursiva(s)). "
                f"Complejidad estimada: **{resultado.get('complejidad_estimada')}**.\n\n"
                f"**Base teórica**: {TEORIA['auditoria_ast']}" + cierre
            )
        filas = []
        for r in resultado.get("comparativa", []):
            estado = " (ABORTADO)" if r.get("abortado") else ""
            filas.append(
                f"- `{r['algoritmo']}` [{r.get('clase')}, {r.get('complejidad')}]: "
                f"{r['metricas']['tiempo_ms']} ms, {r['metricas']['memoria_kb']} KB{estado}"
            )
        clases = {r.get("clase") for r in resultado.get("comparativa", [])}
        teoria = " ".join(TEORIA[c] for c in ("P", "NP", "NSPACE") if c in clases)
        avisos = ("\n\n**Avisos**: " + " ".join(resultado.get("avisos", []))) if resultado.get("avisos") else ""
        return (
            "**Qué se hizo**: se ejecutaron los algoritmos seleccionados sobre el mismo conjunto de datos, de forma secuencial.\n\n"
            "**Resultado**:\n" + "\n".join(filas) + f"\n\n**Base teórica**: {teoria}" + avisos
        )

    if modulo == "varillas":
        rec = resultado.get("recursion", {})
        if rec.get("estado") == "completado":
            rec_txt = (
                f"La recursión ingenua O(2^n) tomó **{rec['metricas']['tiempo_ms']} ms** "
                f"con **{rec['llamadas']}** llamadas recursivas."
            )
        elif rec.get("estado") == "omitido_por_limite":
            rec_txt = rec.get("motivo", "Recursión omitida por límite de seguridad.")
        else:
            rec_txt = "Comparación recursiva desactivada."
        dp_met = resultado.get("tabulacion", {}).get("metricas", {})
        return (
            f"**Qué se hizo**: se resolvió el problema del corte de varillas para longitud n={resultado.get('longitud')}.\n\n"
            f"**Resultado**: ingreso máximo **{resultado.get('ingreso_maximo')}** usando los cortes exactos "
            f"`{resultado.get('cortes_optimos')}`. La tabulación O(n²) tardó **{dp_met.get('tiempo_ms', 0)} ms**. {rec_txt}\n\n"
            f"**Base teórica**: {TEORIA['varillas']}" + cierre
        )

    if modulo == "probabilistas":
        mc = resultado.get("monte_carlo_miller_rabin", {})
        lv = resultado.get("las_vegas_quicksort", {})
        return (
            f"**Qué se hizo**: se comparó Miller-Rabin (Monte Carlo, k={mc.get('rondas_k')}) sobre n={mc.get('numero')} "
            f"contra Quicksort Aleatorizado (Las Vegas) sobre {lv.get('ejecuciones')} corridas de tamaño {lv.get('tamano_arreglo')}.\n\n"
            f"**Resultado**:\n"
            f"- **Miller-Rabin**: **{mc.get('veredicto')}** en {mc.get('rondas_ejecutadas')} ronda(s) "
            f"(cota de error ≤ {mc.get('cota_error_teorica')}, tiempo {mc.get('metricas', {}).get('tiempo_ms', 0)} ms).\n"
            f"- **Quicksort Aleatorizado**: 100% exacto (error 0%), tiempo promedio **{lv.get('tiempo_promedio_ms')} ms** "
            f"(rango {lv.get('tiempo_min_ms')}–{lv.get('tiempo_max_ms')} ms).\n\n"
            f"**Base teórica**: {TEORIA['probabilistas']}" + cierre
        )

    return "Proceso computacional completado con éxito bajo las restricciones del modelo determinista."