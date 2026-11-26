"""Módulo 4: Corte de varillas (Tabulación O(n^2) con reconstrucción vs. Recursión O(2^n))."""
from typing import Any, Dict, List
from backend.core.medicion import medir


def _tabulacion(n: int, precios: List[int]) -> Dict[str, Any]:
    dp = [0] * (n + 1)
    primer_corte = [0] * (n + 1)
    operaciones = 0
    traza: List[Dict[str, Any]] = []

    for j in range(1, n + 1):
        mejor = -1
        corte_elegido = j
        for i in range(1, j + 1):
            operaciones += 1
            candidato = precios[i - 1] + dp[j - i]
            if candidato > mejor:
                mejor = candidato
                corte_elegido = i
        dp[j] = mejor
        primer_corte[j] = corte_elegido
        traza.append({
            "paso": j,
            "descripcion": f"Longitud {j}: ingreso óptimo={mejor} cortando pieza de {corte_elegido} + resto {j - corte_elegido}",
            "subproblema": j,
            "ingreso_optimo": mejor,
            "primer_corte": corte_elegido,
        })

    cortes: List[int] = []
    restante = n
    while restante > 0:
        c = primer_corte[restante]
        cortes.append(c)
        restante -= c

    return {
        "ingreso_maximo": dp[n],
        "cortes": cortes,
        "tabla_dp": dp,
        "primer_corte": primer_corte,
        "operaciones": operaciones,
        "traza": traza,
    }


def _recursivo_ingenuo(n: int, precios: List[int]) -> Dict[str, Any]:
    llamadas = 0

    def resolver(restante: int) -> int:
        nonlocal llamadas
        llamadas += 1
        if restante == 0:
            return 0
        mejor = -1
        for i in range(1, restante + 1):
            cand = precios[i - 1] + resolver(restante - i)
            if cand > mejor:
                mejor = cand
        return mejor

    ingreso = resolver(n)
    return {"ingreso_maximo": ingreso, "llamadas": llamadas}


def ejecutar_corte_varillas(
    longitud: int,
    precios: List[int],
    incluir_recursivo: bool = True,
    limite_recursivo: int = 20,
) -> Dict[str, Any]:
    precios_usados = precios[:longitud]

    res_dp, metricas_dp = medir(_tabulacion, longitud, precios_usados)

    recursivo_info: Dict[str, Any]
    if not incluir_recursivo:
        recursivo_info = {"estado": "no_solicitado"}
    elif longitud > limite_recursivo:
        recursivo_info = {
            "estado": "omitido_por_limite",
            "motivo": f"n={longitud} supera el límite seguro ({limite_recursivo}) para O(2^n).",
            "llamadas_teoricas": 2 ** longitud,
        }
    else:
        res_rec, metricas_rec = medir(_recursivo_ingenuo, longitud, precios_usados)
        recursivo_info = {
            "estado": "completado",
            "ingreso_maximo": res_rec["ingreso_maximo"],
            "llamadas": res_rec["llamadas"],
            "coincide_con_dp": res_rec["ingreso_maximo"] == res_dp["ingreso_maximo"],
            "metricas": metricas_rec,
        }

    # Serie de crecimiento para gráfica comparativa (hasta min(longitud, 16) para respuesta ágil)
    tope_curva = min(longitud, limite_recursivo, 16)
    curva_tamanos: List[int] = []
    curva_dp_ms: List[float] = []
    curva_rec_ms: List[float] = []
    curva_rec_llamadas: List[int] = []

    for tam in range(1, tope_curva + 1):
        _, m_dp = medir(_tabulacion, tam, precios_usados[:tam])
        r_rec, m_rec = medir(_recursivo_ingenuo, tam, precios_usados[:tam])
        curva_tamanos.append(tam)
        curva_dp_ms.append(m_dp["tiempo_ms"])
        curva_rec_ms.append(m_rec["tiempo_ms"])
        curva_rec_llamadas.append(r_rec["llamadas"])

    return {
        "resultado": {
            "longitud": longitud,
            "ingreso_maximo": res_dp["ingreso_maximo"],
            "cortes_optimos": res_dp["cortes"],
            "verificacion_suma_cortes": sum(res_dp["cortes"]),
            "tabulacion": {
                "complejidad": "O(n^2)",
                "operaciones": res_dp["operaciones"],
                "metricas": metricas_dp,
            },
            "recursion": recursivo_info,
        },
        "traza": res_dp["traza"],
        "visualizacion": {
            "tabla_dp": [
                {"longitud": idx, "ingreso": res_dp["tabla_dp"][idx], "corte": res_dp["primer_corte"][idx]}
                for idx in range(1, longitud + 1)
            ],
            "curva_crecimiento": {
                "tamanos": curva_tamanos,
                "tabulacion_ms": curva_dp_ms,
                "recursion_ms": curva_rec_ms,
                "recursion_llamadas": curva_rec_llamadas,
            },
        },
        "metricas": metricas_dp,
    }