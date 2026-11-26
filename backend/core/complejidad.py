import ast
import itertools
import random
import time
import tracemalloc

CATALOGO = {
    "insertion_sort": {"nombre": "Ordenamiento por Inserción", "clase": "P", "tiempo": "O(n²)", "espacio": "O(1)"},
    "merge_sort": {"nombre": "Ordenamiento por Mezcla", "clase": "P", "tiempo": "O(n log n)", "espacio": "O(n)"},
    "tsp_voraz": {"nombre": "Problema del Viajante (TSP Voraz - Vecino Más Cercano)", "clase": "P", "tiempo": "Polinomial O(n²)", "espacio": "O(n)"},
    "subset_sum": {"nombre": "Suma de Subconjuntos (Subset-Sum)", "clase": "NP", "tiempo": "Exponencial O(2^n)", "espacio": "O(n)"},
    "tsp_brute": {"nombre": "Problema del Viajante (TSP Fuerza Bruta)", "clase": "NP", "tiempo": "Exponencial O(n!)", "espacio": "O(n)"},
    "reachability": {"nombre": "Accesibilidad en Grafos (Savitch / NSPACE)", "clase": "NSPACE", "tiempo": "Polinomial en espacio logarítmico", "espacio": "O(log² n)"},
}


def resolver_algoritmo(alg_id: str, datos: list, timeout: float = 5.0) -> dict:
    inicio = time.perf_counter()
    tracemalloc.start()

    abortado = False
    resultado = {}

    try:
        if alg_id == "insertion_sort":
            arr = datos.copy()
            for i in range(1, len(arr)):
                key = arr[i]
                j = i - 1
                while j >= 0 and arr[j] > key:
                    arr[j + 1] = arr[j]
                    j -= 1
                arr[j + 1] = key
            resultado = {"ordenado": arr}

        elif alg_id == "merge_sort":
            def ms(a):
                if len(a) <= 1:
                    return a
                m = len(a) // 2
                left, right = ms(a[:m]), ms(a[m:])
                res, i, j = [], 0, 0
                while i < len(left) and j < len(right):
                    if left[i] <= right[j]:
                        res.append(left[i])
                        i += 1
                    else:
                        res.append(right[j])
                        j += 1
                res.extend(left[i:])
                res.extend(right[j:])
                return res

            resultado = {"ordenado": ms(datos)}

        elif alg_id == "subset_sum":
            if len(datos) > 16:
                datos = datos[:16]
            target = sum(datos) // 2
            encontrado = False
            subset = []

            n = len(datos)
            for i in range(1 << n):
                if time.perf_counter() - inicio > timeout:
                    abortado = True
                    break
                s = sum(datos[j] for j in range(n) if (i & (1 << j)))
                if s == target:
                    encontrado = True
                    subset = [datos[j] for j in range(n) if (i & (1 << j))]
                    break
            resultado = {
                "objetivo": target,
                "encontrado": encontrado,
                "certificado": subset,
                "n_usado": n,
                "verificado": (sum(subset) == target) if encontrado else None,
            }

        elif alg_id == "tsp_brute":
            if len(datos) > 10:
                datos = datos[:10]
            n = len(datos)
            min_cost = float("inf")
            best_path = []
            for perm in itertools.permutations(range(n)):
                if time.perf_counter() - inicio > timeout:
                    abortado = True
                    break
                cost = sum(abs(datos[perm[i]] - datos[perm[(i + 1) % n]]) for i in range(n))
                if cost < min_cost:
                    min_cost = cost
                    best_path = list(perm)
            resultado = {"min_costo": min_cost, "certificado": best_path, "n_usado": n}

        elif alg_id == "tsp_voraz":
            n = len(datos)
            visitados = [False] * n
            ruta = [0]
            visitados[0] = True
            costo_total = 0
            actual = 0

            for _ in range(n - 1):
                if time.perf_counter() - inicio > timeout:
                    abortado = True
                    break
                mejor_sig = -1
                mejor_dist = float("inf")
                for cand in range(n):
                    if not visitados[cand]:
                        dist = abs(datos[actual] - datos[cand])
                        if dist < mejor_dist:
                            mejor_dist = dist
                            mejor_sig = cand
                visitados[mejor_sig] = True
                ruta.append(mejor_sig)
                costo_total += mejor_dist
                actual = mejor_sig

            if not abortado and n > 1:
                costo_total += abs(datos[actual] - datos[0])

            resultado = {
                "min_costo": costo_total,
                "certificado": ruta,
                "n_usado": n,
                "nota": "Aproximación voraz O(n^2); no garantiza óptimo global frente a TSP Exacto O(n!).",
            }

        elif alg_id == "reachability":
            n = max(2, min(len(datos), 10))
            rng = random.Random(sum(datos) if datos else 1)
            aristas = {(i, rng.randrange(n)) for i in range(n) for _ in range(2)}
            aristas.update((i, i + 1) for i in range(n - 1) if rng.random() < 0.6)
            ady = {i: [b for a, b in aristas if a == i] for i in range(n)}
            k_max = max(1, (n - 1).bit_length())
            llamadas = [0]

            def savitch(u, v, k):
                llamadas[0] += 1
                if time.perf_counter() - inicio > timeout:
                    raise TimeoutError
                if u == v or v in ady[u]:
                    return True
                if k == 0:
                    return False
                return any(savitch(u, w, k - 1) and savitch(w, v, k - 1) for w in range(n))

            try:
                alcanzable = savitch(0, n - 1, k_max)
            except TimeoutError:
                abortado, alcanzable = True, None

            alc_bfs, cola = {0}, [0]
            while cola:
                x = cola.pop()
                for y in ady[x]:
                    if y not in alc_bfs:
                        alc_bfs.add(y)
                        cola.append(y)

            resultado = {
                "origen": 0,
                "destino": n - 1,
                "n_usado": n,
                "alcanzable": alcanzable,
                "coincide_con_bfs": (alcanzable == ((n - 1) in alc_bfs)) if alcanzable is not None else None,
                "llamadas_recursivas": llamadas[0],
                "profundidad_max": k_max,
            }

        else:
            raise ValueError(f"Algoritmo '{alg_id}' desconocido.")

    except Exception as e:
        abortado = True
        resultado = {"error": str(e)}

    fin = time.perf_counter()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "algoritmo": alg_id,
        "abortado": abortado,
        "resultado": resultado,
        "metricas": {
            "tiempo_ms": round((fin - inicio) * 1000, 4),
            "memoria_kb": round(peak / 1024, 2),
        },
    }


def auditar_codigo_ast(codigo: str) -> dict:
    """Analiza estáticamente código Python usando ast para detectar bucles anidados y recursión."""
    try:
        arbol = ast.parse(codigo)
    except SyntaxError as e:
        raise ValueError(f"Error de sintaxis en línea {e.lineno}: {e.msg}")

    bucles = []
    funciones_recursivas = []
    traza = []
    max_profundidad = [0]

    def recorrer(nodo, prof_actual, fn_actual=None):
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
            llamadas_propias = 0
            for sub in ast.walk(nodo):
                if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) and sub.func.id == nodo.name:
                    llamadas_propias += 1
            if llamadas_propias > 0:
                funciones_recursivas.append({"funcion": nodo.name, "linea": nodo.lineno, "llamadas_internas": llamadas_propias})
                traza.append({
                    "paso": len(traza) + 1,
                    "descripcion": f"Recursión detectada en '{nodo.name}' (línea {nodo.lineno}) con {llamadas_propias} llamada(s) recursiva(s).",
                })
            for hijo in ast.iter_child_nodes(nodo):
                recorrer(hijo, prof_actual, nodo.name)
            return

        if isinstance(nodo, (ast.For, ast.AsyncFor, ast.While)):
            nueva_prof = prof_actual + 1
            if nueva_prof > max_profundidad[0]:
                max_profundidad[0] = nueva_prof
            tipo = type(nodo).__name__
            bucles.append({"tipo": tipo, "linea": nodo.lineno, "profundidad": nueva_prof, "funcion": fn_actual or "<global>"})
            traza.append({
                "paso": len(traza) + 1,
                "descripcion": f"Bucle {tipo} en línea {nodo.lineno} (nivel de anidación {nueva_prof}).",
            })
            for hijo in ast.iter_child_nodes(nodo):
                recorrer(hijo, nueva_prof, fn_actual)
            return

        if isinstance(nodo, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            nueva_prof = prof_actual + len(nodo.generators)
            if nueva_prof > max_profundidad[0]:
                max_profundidad[0] = nueva_prof
            bucles.append({"tipo": type(nodo).__name__, "linea": nodo.lineno, "profundidad": nueva_prof, "funcion": fn_actual or "<global>"})
            traza.append({
                "paso": len(traza) + 1,
                "descripcion": f"Comprensión {type(nodo).__name__} en línea {nodo.lineno} ({len(nodo.generators)} generador(es), profundidad {nueva_prof}).",
            })

        for hijo in ast.iter_child_nodes(nodo):
            recorrer(hijo, prof_actual, fn_actual)

    recorrer(arbol, 0)

    max_rec = max((f["llamadas_internas"] for f in funciones_recursivas), default=0)
    if max_rec >= 2:
        estimacion, clase = "O(2^n) (Exponencial por ramificación recursiva)", "Exponencial / NP"
    elif max_profundidad[0] == 0 and max_rec == 1:
        estimacion, clase = "O(n) (Recursión lineal)", "P"
    elif max_profundidad[0] == 0:
        estimacion, clase = "O(1) (Constante)", "P"
    elif max_profundidad[0] == 1:
        estimacion, clase = "O(n) (Lineal)", "P"
    else:
        estimacion, clase = f"O(n^{max_profundidad[0]}) (Polinomial de grado {max_profundidad[0]})", "P"

    return {
        "resultado": {
            "profundidad_max_bucles": max_profundidad[0],
            "total_bucles": len(bucles),
            "bucles": bucles,
            "funciones_recursivas": funciones_recursivas,
            "complejidad_estimada": estimacion,
            "clase_estimada": clase,
            "nodos_ast_analizados": sum(1 for _ in ast.walk(arbol)),
        },
        "traza": traza or [{"paso": 1, "descripcion": "No se detectaron bucles ni recursión; complejidad constante O(1)."}],
    }