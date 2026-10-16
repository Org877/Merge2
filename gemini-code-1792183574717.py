import itertools
from typing import Dict, List, Set, Tuple

def analizar_cadena(w: str) -> dict:
    return {
        "longitud": len(w),
        "inversa": w[::-1],
        "conteo_simbolos": {s: w.count(s) for s in set(w)},
        "prefijos": [w[:i] for i in range(len(w) + 1)],
        "sufijos": [w[i:] for i in range(len(w) + 1)],
    }

def operar_lenguajes(op: str, L: List[str], M: List[str], sigma: List[str], k: int) -> dict:
    set_L, set_M = set(L), set(M)
    sigma_set = set(sigma)
    
    if op == "union":
        res = set_L.union(set_M)
    elif op == "interseccion":
        res = set_L.intersection(set_M)
    elif op == "diferencia":
        res = set_L.difference(set_M)
    elif op == "concatenacion":
        res = {x + y for x in set_L for y in set_M}
    elif op == "potencia_n":
        res = {""} if k == 0 else set_L
        for _ in range(k - 1):
            res = {x + y for x in res for y in set_L}
    elif op == "clausura_positiva":
        res = set()
        curr = set_L
        for _ in range(max(1, k)):
            res.update(curr)
            curr = {x + y for x in curr for y in set_L}
    elif op == "complemento":
        universo = {""}
        for length in range(1, k + 1):
            universo.update({"".join(c) for c in itertools.product(sigma_set, repeat=length)})
        res = universo.difference(set_L)
    elif op == "inversa":
        res = {x[::-1] for x in set_L}
    else:
        res = set_L
    return sorted(list(res))

def simular_automata(req) -> dict:
    estados = set(req.estados)
    alfabeto = set(req.alfabeto)
    inicial = req.estado_inicial
    aceptacion = set(req.estados_aceptacion)
    
    if inicial not in estados:
        raise ValueError(f"El estado inicial '{inicial}' no pertenece al conjunto de estados.")
    for ac in aceptacion:
        if ac not in estados:
            raise ValueError(f"El estado de aceptación '{ac}' no pertenece al conjunto de estados.")

    traza = []
    
    if req.tipo == "afd":
        actual = inicial
        recorrido = [actual]
        traza.append({"paso": 0, "descripcion": f"Estado inicial: {actual}", "estado": actual})
        
        for idx, simbolo in enumerate(req.palabra):
            if simbolo not in alfabeto:
                raise ValueError(f"Símbolo '{simbolo}' no forma parte del alfabeto.")
            trans = req.transiciones.get(actual, {})
            destino_lista = trans.get(simbolo, [])
            if not destino_lista:
                return {"pertenece": False, "traza": traza, "recorrido": recorrido, "motivo": f"Transición bloqueada en '{simbolo}' desde '{actual}'."}
            actual = destino_lista[0]
            recorrido.append(actual)
            traza.append({"paso": idx + 1, "descripcion": f"Lee '{simbolo}', transiciona a {actual}", "estado": actual})
            
        pertenece = actual in aceptacion
        return {"pertenece": pertenece, "traza": traza, "recorrido": recorrido, "estado_final": actual}

    elif req.tipo in ["afnd", "afnde"]:
        # Simulación con conjuntos de estados activos y epsilon-clausura si aplica
        def obtener_epsilon_clausura(ESTS: Set[str]) -> Set[str]:
            cierre = set(ESTS)
            pila = list(ESTS)
            while pila:
                e = pila.pop()
                eps_destinos = req.transiciones.get(e, {}).get("eps", [])
                for d in eps_destinos:
                    if d not in cierre:
                        cierre.add(d)
                        pila.append(d)
            return cierre

        activos = obtener_epsilon_clausura({inicial})
        traza.append({"paso": 0, "descripcion": f"Estados activos iniciales (con ε-clausura): {list(activos)}", "estados": list(activos)})
        recorrido = [list(activos)]

        for idx, simbolo in enumerate(req.palabra):
            siguientes = set()
            for est in activos:
                destinos = req.transiciones.get(est, {}).get(simbolo, [])
                for d in destinos:
                    siguientes.add(d)
            activos = obtener_epsilon_clausura(siguientes)
            recorrido.append(list(activos))
            traza.append({"paso": idx + 1, "descripcion": f"Lee '{simbolo}', nuevos activos: {list(activos)}", "estados": list(activos)})
            if not activos:
                break

        pertenece = any(est in aceptacion for est in activos)
        return {"pertenece": pertenece, "traza": traza, "recorrido_estados": recorrido}