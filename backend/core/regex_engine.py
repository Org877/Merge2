"""Módulo 1: Conversión Regex -> AFN-ε (Thompson) -> AFD (Subconjuntos) y simulación."""
from collections import deque
from typing import Any, Dict, FrozenSet, List, Set, Tuple


def _insertar_concatenacion(regex: str) -> str:
    limpia = regex.replace(" ", "")
    if not limpia:
        raise ValueError("La expresión regular no puede estar vacía.")
    salida: List[str] = []
    for i, c1 in enumerate(limpia):
        salida.append(c1)
        if i + 1 < len(limpia):
            c2 = limpia[i + 1]
            c1_cierra = c1 not in ("(", "|")
            c2_abre = c2 not in ("|", ")", "*", "+", "?")
            if c1_cierra and c2_abre:
                salida.append(".")
    return "".join(salida)


def _a_postfija(regex: str) -> str:
    expr = _insertar_concatenacion(regex)
    prec = {"|": 1, ".": 2, "*": 3, "+": 3, "?": 3}
    salida: List[str] = []
    pila: List[str] = []

    for c in expr:
        if c == "(":
            pila.append(c)
        elif c == ")":
            while pila and pila[-1] != "(":
                salida.append(pila.pop())
            if not pila:
                raise ValueError("Paréntesis de cierre ')' sin apertura correspondiente.")
            pila.pop()
        elif c in prec:
            while pila and pila[-1] != "(" and prec.get(pila[-1], 0) >= prec[c]:
                salida.append(pila.pop())
            pila.append(c)
        else:
            salida.append(c)

    while pila:
        tope = pila.pop()
        if tope == "(":
            raise ValueError("Paréntesis de apertura '(' sin cerrar.")
        salida.append(tope)

    return "".join(salida)


def _thompson_afne(postfija: str) -> Dict[str, Any]:
    contador = [0]
    transiciones: Dict[str, Dict[str, List[str]]] = {}
    alfabeto: Set[str] = set()

    def nuevo_estado() -> str:
        eid = f"n{contador[0]}"
        contador[0] += 1
        transiciones[eid] = {}
        return eid

    def agregar_trans(origen: str, simbolo: str, destino: str) -> None:
        transiciones.setdefault(origen, {}).setdefault(simbolo, [])
        if destino not in transiciones[origen][simbolo]:
            transiciones[origen][simbolo].append(destino)

    pila: List[Tuple[str, str]] = []

    for tok in postfija:
        if tok == ".":
            if len(pila) < 2:
                raise ValueError("Expresión regular inválida: falta operando en concatenación.")
            s2, e2 = pila.pop()
            s1, e1 = pila.pop()
            agregar_trans(e1, "eps", s2)
            pila.append((s1, e2))
        elif tok == "|":
            if len(pila) < 2:
                raise ValueError("Expresión regular inválida: falta operando en unión '|'.")
            s2, e2 = pila.pop()
            s1, e1 = pila.pop()
            s, e = nuevo_estado(), nuevo_estado()
            agregar_trans(s, "eps", s1)
            agregar_trans(s, "eps", s2)
            agregar_trans(e1, "eps", e)
            agregar_trans(e2, "eps", e)
            pila.append((s, e))
        elif tok == "*":
            if not pila:
                raise ValueError("Expresión regular inválida: '*' sin operando.")
            s1, e1 = pila.pop()
            s, e = nuevo_estado(), nuevo_estado()
            agregar_trans(s, "eps", s1)
            agregar_trans(s, "eps", e)
            agregar_trans(e1, "eps", s1)
            agregar_trans(e1, "eps", e)
            pila.append((s, e))
        elif tok == "+":
            if not pila:
                raise ValueError("Expresión regular inválida: '+' sin operando.")
            s1, e1 = pila.pop()
            s, e = nuevo_estado(), nuevo_estado()
            agregar_trans(s, "eps", s1)
            agregar_trans(e1, "eps", s1)
            agregar_trans(e1, "eps", e)
            pila.append((s, e))
        elif tok == "?":
            if not pila:
                raise ValueError("Expresión regular inválida: '?' sin operando.")
            s1, e1 = pila.pop()
            s, e = nuevo_estado(), nuevo_estado()
            agregar_trans(s, "eps", s1)
            agregar_trans(s, "eps", e)
            agregar_trans(e1, "eps", e)
            pila.append((s, e))
        else:
            s, e = nuevo_estado(), nuevo_estado()
            sim = "eps" if tok == "ε" else tok
            if sim != "eps":
                alfabeto.add(sim)
            agregar_trans(s, sim, e)
            pila.append((s, e))

    if len(pila) != 1:
        raise ValueError("Expresión regular mal formada.")

    inicio, aceptacion = pila[0]
    return {
        "estados": list(transiciones.keys()),
        "alfabeto": sorted(alfabeto),
        "transiciones": transiciones,
        "estado_inicial": inicio,
        "estados_aceptacion": [aceptacion],
    }


def _clausura_eps(estados: Set[str], trans: Dict[str, Dict[str, List[str]]]) -> FrozenSet[str]:
    visitados = set(estados)
    pila = list(estados)
    while pila:
        actual = pila.pop()
        for dest in trans.get(actual, {}).get("eps", []):
            if dest not in visitados:
                visitados.add(dest)
                pila.append(dest)
    return frozenset(visitados)


def _subconjuntos_afd(afne: Dict[str, Any]) -> Dict[str, Any]:
    trans_nfa = afne["transiciones"]
    alfabeto = afne["alfabeto"]
    acept_nfa = set(afne["estados_aceptacion"])

    inicial_set = _clausura_eps({afne["estado_inicial"]}, trans_nfa)
    mapa_nombres: Dict[FrozenSet[str], str] = {inicial_set: "q0"}
    cola: deque[FrozenSet[str]] = deque([inicial_set])

    trans_afd: Dict[str, Dict[str, List[str]]] = {"q0": {}}
    acept_afd: List[str] = []
    composicion: Dict[str, List[str]] = {"q0": sorted(inicial_set)}
    traza_conv: List[Dict[str, Any]] = []

    while cola:
        conjunto = cola.popleft()
        nombre = mapa_nombres[conjunto]
        if conjunto & acept_nfa:
            acept_afd.append(nombre)

        for sim in alfabeto:
            alcanzados: Set[str] = set()
            for st in conjunto:
                alcanzados.update(trans_nfa.get(st, {}).get(sim, []))
            if not alcanzados:
                continue
            destino_set = _clausura_eps(alcanzados, trans_nfa)
            if destino_set not in mapa_nombres:
                nuevo_nombre = f"q{len(mapa_nombres)}"
                mapa_nombres[destino_set] = nuevo_nombre
                trans_afd[nuevo_nombre] = {}
                composicion[nuevo_nombre] = sorted(destino_set)
                cola.append(destino_set)
            dest_nombre = mapa_nombres[destino_set]
            trans_afd[nombre][sim] = [dest_nombre]
            traza_conv.append({
                "paso": len(traza_conv) + 1,
                "descripcion": f"Subconjuntos: δ({nombre}, '{sim}') = {dest_nombre} {sorted(destino_set)}",
            })

    return {
        "estados": list(trans_afd.keys()),
        "alfabeto": alfabeto,
        "transiciones": trans_afd,
        "estado_inicial": "q0",
        "estados_aceptacion": acept_afd,
        "composicion_estados": composicion,
        "traza_conversion": traza_conv,
    }


def _agrupar_aristas_dict(transiciones: Dict[str, Dict[str, List[str]]]) -> List[Dict[str, str]]:
    grupos: Dict[Tuple[str, str], List[str]] = {}
    for origen, trans in transiciones.items():
        for sim, destinos in trans.items():
            etiqueta = "ε" if sim in ("eps", "ε") else sim
            for d in destinos:
                grupos.setdefault((origen, d), []).append(etiqueta)
    return [
        {"origen": o, "destino": d, "simbolo": ",".join(sorted(sims))}
        for (o, d), sims in grupos.items()
    ]


def convertir_y_simular_regex(regex: str, palabra: str) -> Dict[str, Any]:
    postfija = _a_postfija(regex)
    afne = _thompson_afne(postfija)
    afd = _subconjuntos_afd(afne)

    actual = afd["estado_inicial"]
    recorrido: List[List[str]] = [[actual]]
    traza_sim: List[Dict[str, Any]] = [{
        "paso": 1,
        "descripcion": f"Inicio de simulación en {actual} (subconjunto AFN-ε: {afd['composicion_estados'][actual]}).",
    }]
    rechazada_en_camino = False

    for idx, ch in enumerate(palabra, start=1):
        destinos = afd["transiciones"].get(actual, {}).get(ch, [])
        if not destinos:
            traza_sim.append({
                "paso": len(traza_sim) + 1,
                "descripcion": f"Carácter #{idx} '{ch}': sin transición definida desde {actual}. Cadena rechazada.",
            })
            rechazada_en_camino = True
            break
        siguiente = destinos[0]
        traza_sim.append({
            "paso": len(traza_sim) + 1,
            "descripcion": f"Carácter #{idx} '{ch}': {actual} -> {siguiente}.",
        })
        actual = siguiente
        recorrido.append([actual])

    aceptada = (not rechazada_en_camino) and (actual in afd["estados_aceptacion"])
    veredicto = "ACEPTADA" if aceptada else "RECHAZADA"
    traza_sim.append({
        "paso": len(traza_sim) + 1,
        "descripcion": f"Fin de cadena en estado {actual}. Veredicto final: {veredicto}.",
    })

    return {
        "resultado": {
            "regex": regex,
            "postfija": postfija,
            "palabra": palabra,
            "aceptada": aceptada,
            "veredicto": veredicto,
            "estado_final": actual,
            "resumen_afn_epsilon": {
                "num_estados": len(afne["estados"]),
                "estado_inicial": afne["estado_inicial"],
                "estados_aceptacion": afne["estados_aceptacion"],
                "alfabeto": afne["alfabeto"],
            },
            "afd": {
                "num_estados": len(afd["estados"]),
                "estados": afd["estados"],
                "alfabeto": afd["alfabeto"],
                "estado_inicial": afd["estado_inicial"],
                "estados_aceptacion": afd["estados_aceptacion"],
                "transiciones": afd["transiciones"],
                "composicion_estados": afd["composicion_estados"],
            },
        },
        "traza": afd["traza_conversion"] + traza_sim,
        "visualizacion": {
            "nodos": [
                {"id": e, "inicial": e == afd["estado_inicial"], "aceptacion": e in afd["estados_aceptacion"]}
                for e in afd["estados"]
            ],
            "aristas": _agrupar_aristas_dict(afd["transiciones"]),
            "recorrido": recorrido,
            "afn_epsilon": {
                "nodos": [
                    {"id": e, "inicial": e == afne["estado_inicial"], "aceptacion": e in afne["estados_aceptacion"]}
                    for e in afne["estados"]
                ],
                "aristas": _agrupar_aristas_dict(afne["transiciones"]),
            },
        },
    }