import random

from fastapi import APIRouter, HTTPException

from backend.core.complejidad import CATALOGO, auditar_codigo_ast, resolver_algoritmo
from backend.core.medicion import _candado, medir
from backend.schemas import AuditoriaCodigoRequest, BenchmarkRequest, ContratoRespuesta

router = APIRouter(prefix="/api/complejidad", tags=["Módulo 3: Complejidad"])

TAM_MAX = 5000
LIMITE_NP = {"subset_sum": 16, "tsp_brute": 10, "reachability": 10}
SERIE_P = [100, 250, 500, 1000, 2000]


def _datos(n: int, semilla: int):
    rng = random.Random(semilla)
    return [rng.randint(1, 10000) for _ in range(n)]


@router.get("/catalogo")
def catalogo():
    return [{"id": k, **v} for k, v in CATALOGO.items()]


@router.post("/benchmark", response_model=ContratoRespuesta)
def benchmark(req: BenchmarkRequest):
    if len(req.algoritmos) < 2:
        raise HTTPException(status_code=400, detail="Selecciona al menos 2 algoritmos para compararlos.")
    desconocidos = [a for a in req.algoritmos if a not in CATALOGO]
    if desconocidos:
        raise HTTPException(status_code=400, detail=f"Algoritmo(s) desconocido(s): {', '.join(desconocidos)}.")

    avisos = []
    if req.datos_personalizados:
        datos = list(req.datos_personalizados)
    else:
        n = max(2, req.tamano)
        if n > TAM_MAX:
            avisos.append(f"El tamaño se limitó a {TAM_MAX} para proteger al servidor.")
            n = TAM_MAX
        datos = _datos(n, req.semilla)

    comparativa = []
    with _candado:
        for alg in req.algoritmos:
            r = resolver_algoritmo(alg, datos, req.timeout_segundos)
            r["clase"] = CATALOGO[alg]["clase"]
            r["complejidad"] = CATALOGO[alg]["tiempo"]
            if alg in LIMITE_NP and len(datos) > LIMITE_NP[alg]:
                avisos.append(f"{CATALOGO[alg]['nombre']}: se usaron solo {LIMITE_NP[alg]} elementos (límite exponencial).")
            if r["abortado"]:
                avisos.append(f"{CATALOGO[alg]['nombre']}: abortado por tiempo límite ({req.timeout_segundos} s) o error.")
            comparativa.append(r)

        series = []
        if req.incluir_series:
            for alg in req.algoritmos:
                tams = [t for t in (req.tamanos_serie or SERIE_P) if t <= TAM_MAX]
                if alg in LIMITE_NP:
                    tams = list(range(4, LIMITE_NP[alg] + 1, 2))
                xs, ts, ms = [], [], []
                for t in tams:
                    r = resolver_algoritmo(alg, _datos(t, req.semilla), min(req.timeout_segundos, 2.0))
                    xs.append(t); ts.append(r["metricas"]["tiempo_ms"]); ms.append(r["metricas"]["memoria_kb"])
                    if r["abortado"]:
                        avisos.append(f"Serie de {CATALOGO[alg]['nombre']} cortada en n={t} por tiempo límite.")
                        break
                series.append({"algoritmo": alg, "clase": CATALOGO[alg]["clase"], "tamanos": xs, "tiempos_ms": ts, "memoria_kb": ms})

    resumen = []
    for r in comparativa:
        res = r["resultado"]
        if "ordenado" in res:
            res = {"primeros_10": res["ordenado"][:10], "n": len(res["ordenado"])}
        resumen.append({**r, "resultado": res})

    return ContratoRespuesta(
        modulo="complejidad",
        operacion="benchmark",
        entrada={"algoritmos": req.algoritmos, "tamano": len(datos), "semilla": req.semilla},
        resultado={"comparativa": resumen, "avisos": avisos},
        visualizacion={
            "series": series,
            "barras": [{"algoritmo": r["algoritmo"], "clase": r["clase"], **r["metricas"]} for r in comparativa],
        },
        metricas={
            "tiempo_ms": round(sum(r["metricas"]["tiempo_ms"] for r in comparativa), 4),
            "memoria_kb": max(r["metricas"]["memoria_kb"] for r in comparativa),
        },
    )


@router.post("/auditar", response_model=ContratoRespuesta)
def auditar_codigo(req: AuditoriaCodigoRequest):
    try:
        salida, met = medir(auditar_codigo_ast, req.codigo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ContratoRespuesta(
        modulo="complejidad",
        operacion="auditar_ast",
        entrada={"lineas": len(req.codigo.splitlines())},
        resultado=salida["resultado"],
        traza=salida["traza"],
        visualizacion={"bucles": salida["resultado"]["bucles"]},
        metricas=met,
    )
