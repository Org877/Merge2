"""Módulo 5: Benchmark de algoritmos probabilistas (Monte Carlo vs. Las Vegas)."""
import random
from typing import Any, Dict, List
from backend.core.medicion import medir


def _miller_rabin_una_corrida(n: int, k: int, rng: random.Random) -> Dict[str, Any]:
    if n < 2:
        return {"es_probablemente_primo": False, "rondas_ejecutadas": 0, "traza": [{"paso": 1, "descripcion": f"{n} < 2, es compuesto."}]}
    if n in (2, 3):
        return {"es_probablemente_primo": True, "rondas_ejecutadas": 0, "traza": [{"paso": 1, "descripcion": f"{n} es primo base."}]}
    if n % 2 == 0:
        return {"es_probablemente_primo": False, "rondas_ejecutadas": 0, "traza": [{"paso": 1, "descripcion": f"{n} es par > 2, es compuesto."}]}

    # Descomposición n - 1 = 2^s * d
    s = 0
    d = n - 1
    while d % 2 == 0:
        d //= 2
        s += 1

    traza: List[Dict[str, Any]] = [{
        "paso": 1,
        "descripcion": f"Descomposición: {n} - 1 = 2^{s} * {d}",
    }]

    for ronda in range(1, k + 1):
        a = rng.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            traza.append({
                "paso": ronda + 1,
                "descripcion": f"Ronda {ronda} (base a={a}): a^d mod n = {x}. No es testigo; continúa.",
            })
            continue

        paso_ronda = False
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                paso_ronda = True
                break

        if not paso_ronda:
            traza.append({
                "paso": ronda + 1,
                "descripcion": f"Ronda {ronda} (base a={a}): TESTIGO DE COMPOSICIÓN encontrado. {n} es compuesto con certeza.",
            })
            return {
                "es_probablemente_primo": False,
                "rondas_ejecutadas": ronda,
                "testigo": a,
                "traza": traza,
            }

        traza.append({
            "paso": ronda + 1,
            "descripcion": f"Ronda {ronda} (base a={a}): alcanzó n-1 al elevar al cuadrado. Pasa la ronda.",
        })

    return {
        "es_probablemente_primo": True,
        "rondas_ejecutadas": k,
        "testigo": None,
        "traza": traza,
    }


def _quicksort_aleatorizado(arr: List[int], rng: random.Random) -> Dict[str, Any]:
    """Quicksort aleatorizado iterativo de 3 vías (Las Vegas: siempre correcto, tiempo aleatorio)."""
    datos = list(arr)
    comparaciones = 0
    pivotes_elegidos = 0
    pila = [(0, len(datos) - 1)]

    while pila:
        izq, der = pila.pop()
        if izq >= der:
            continue

        idx_pivote = rng.randint(izq, der)
        pivote = datos[idx_pivote]
        pivotes_elegidos += 1

        lt, i, gt = izq, izq, der
        while i <= gt:
            comparaciones += 1
            if datos[i] < pivote:
                datos[lt], datos[i] = datos[i], datos[lt]
                lt += 1
                i += 1
            elif datos[i] > pivote:
                datos[i], datos[gt] = datos[gt], datos[i]
                gt -= 1
            else:
                i += 1

        if izq < lt - 1:
            pila.append((izq, lt - 1))
        if gt + 1 < der:
            pila.append((gt + 1, der))

    return {
        "ordenado": datos,
        "comparaciones": comparaciones,
        "pivotes_elegidos": pivotes_elegidos,
    }


def _curva_error_monte_carlo(k_max: int, semilla: int) -> Dict[str, Any]:
    """Evalúa error teórico 4^-k y tasa empírica de falsos primos en Carmichael n=561."""
    rng = random.Random(semilla + 999)
    carmichael = 561  # Compuesto (3*11*17) que engaña a Fermat, ideal para ilustrar Miller-Rabin
    ensayos = 120
    rondas_eje = list(range(1, min(k_max, 12) + 1))
    error_teorico = [round(4 ** (-r), 8) for r in rondas_eje]
    error_empirico: List[float] = []

    for r in rondas_eje:
        falsos_primos = 0
        for _ in range(ensayos):
            if _miller_rabin_una_corrida(carmichael, r, rng)["es_probablemente_primo"]:
                falsos_primos += 1
        error_empirico.append(round(falsos_primos / ensayos, 4))

    return {
        "rondas": rondas_eje,
        "cota_teorica_4_menos_k": error_teorico,
        "error_empirico_carmichael_561": error_empirico,
        "ensayos_por_ronda": ensayos,
    }


def ejecutar_benchmark_probabilistas(
    numero: int,
    rondas_k: int,
    tamano_arreglo: int,
    ejecuciones_las_vegas: int,
    semilla: int = 42,
) -> Dict[str, Any]:
    rng_mr = random.Random(semilla)
    res_mr, metricas_mr = medir(_miller_rabin_una_corrida, numero, rondas_k, rng_mr)

    cota_error = 4 ** (-rondas_k) if res_mr["es_probablemente_primo"] else 0.0

    # Arreglo reproducible para Quicksort Aleatorizado (Las Vegas)
    rng_datos = random.Random(semilla)
    arreglo_base = [rng_datos.randint(0, tamano_arreglo * 10) for _ in range(tamano_arreglo)]
    referencia_ordenada = sorted(arreglo_base)

    corridas_lv: List[Dict[str, Any]] = []
    for idx in range(1, ejecuciones_las_vegas + 1):
        rng_qs = random.Random(semilla + idx * 31)
        res_qs, met_qs = medir(_quicksort_aleatorizado, arreglo_base, rng_qs)
        es_exacto = res_qs["ordenado"] == referencia_ordenada
        corridas_lv.append({
            "corrida": idx,
            "exacto": es_exacto,
            "comparaciones": res_qs["comparaciones"],
            "pivotes_elegidos": res_qs["pivotes_elegidos"],
            "tiempo_ms": met_qs["tiempo_ms"],
            "memoria_kb": met_qs["memoria_kb"],
        })

    tiempos_lv = [c["tiempo_ms"] for c in corridas_lv]
    memorias_lv = [c["memoria_kb"] for c in corridas_lv]
    tiempo_prom_lv = round(sum(tiempos_lv) / len(tiempos_lv), 4)
    mem_prom_lv = round(sum(memorias_lv) / len(memorias_lv), 2)

    curva_error = _curva_error_monte_carlo(rondas_k, semilla)

    traza = list(res_mr["traza"])
    traza.append({
        "paso": len(traza) + 1,
        "descripcion": (
            f"Quicksort Aleatorizado (Las Vegas): {ejecuciones_las_vegas} corridas sobre n={tamano_arreglo}; "
            f"100% exactas, tiempo promedio={tiempo_prom_lv} ms (rango {min(tiempos_lv)}-{max(tiempos_lv)} ms)."
        ),
    })

    return {
        "resultado": {
            "monte_carlo_miller_rabin": {
                "tipo": "Monte Carlo (tiempo fijo, error acotado)",
                "numero": numero,
                "rondas_k": rondas_k,
                "veredicto": "PROBABLEMENTE PRIMO" if res_mr["es_probablemente_primo"] else "COMPUESTO",
                "rondas_ejecutadas": res_mr["rondas_ejecutadas"],
                "testigo": res_mr.get("testigo"),
                "cota_error_teorica": cota_error,
                "metricas": metricas_mr,
            },
            "las_vegas_quicksort": {
                "tipo": "Las Vegas (resultado 100% exacto, tiempo variable)",
                "tamano_arreglo": tamano_arreglo,
                "ejecuciones": ejecuciones_las_vegas,
                "todas_exactas": all(c["exacto"] for c in corridas_lv),
                "tasa_error": 0.0,
                "tiempo_promedio_ms": tiempo_prom_lv,
                "tiempo_min_ms": min(tiempos_lv),
                "tiempo_max_ms": max(tiempos_lv),
                "memoria_promedio_kb": mem_prom_lv,
                "corridas": corridas_lv,
            },
        },
        "traza": traza,
        "visualizacion": {
            "curva_error_monte_carlo": curva_error,
            "tiempos_las_vegas": {
                "etiquetas": [f"Corrida {c['corrida']}" for c in corridas_lv],
                "tiempos_ms": tiempos_lv,
                "comparaciones": [c["comparaciones"] for c in corridas_lv],
            },
        },
        "metricas": {
            "tiempo_ms": round(metricas_mr["tiempo_ms"] + sum(tiempos_lv), 4),
            "memoria_kb": max(metricas_mr["memoria_kb"], max(memorias_lv)),
        },
    }