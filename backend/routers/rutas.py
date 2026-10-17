from fastapi import APIRouter, HTTPException

from backend.core.grafos import alcance_maximo, ejecutar_busqueda_grafo
from backend.core.medicion import medir
from backend.schemas import ContratoRespuesta, GrafoRequest

router = APIRouter(prefix="/api/rutas", tags=["Módulo 2: Rutas y grafos"])

ALGORITMOS = {"bfs", "dfs", "dijkstra", "star", "greedy", "hill"}


@router.post("/buscar", response_model=ContratoRespuesta)
def buscar(req: GrafoRequest):
    vis_base = {
        "nodos": sorted({str(n) for n in req.grafo} | {str(v) for ady in req.grafo.values() for v, _ in ady}),
        "aristas": [{"origen": str(u), "destino": str(v), "peso": p} for u, ady in req.grafo.items() for v, p in ady],
        "dirigido": req.dirigido,
    }

    # ---- Modo alcance máximo ----
    if req.modo == "alcance":
        try:
            res, met = medir(alcance_maximo, req.grafo, req.origen, req.dirigido)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return ContratoRespuesta(
            modulo="rutas", operacion="alcance_maximo", entrada=req.model_dump(),
            resultado=res, traza=res["traza"],
            visualizacion={**vis_base, "origen": req.origen, "alcanzables": res["alcanzables"],
                           "camino": [], "orden_visita": res["orden_visita"]},
            metricas=met,
        )

    # ---- Modo búsqueda de ruta (uno o varios algoritmos sobre el mismo grafo) ----
    desconocidos = [a for a in req.algoritmos if a not in ALGORITMOS]
    if desconocidos:
        raise HTTPException(status_code=400, detail=f"Algoritmo(s) no soportado(s): {', '.join(desconocidos)}.")
    if not req.algoritmos:
        raise HTTPException(status_code=400, detail="Selecciona al menos un algoritmo.")

    comparativa, principal, traza_principal = [], None, []
    for alg in req.algoritmos:
        try:
            res, met = medir(ejecutar_busqueda_grafo, req.grafo, req.origen, req.destino,
                             req.dirigido, alg, req.heuristica, req.reinicios)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        existe = bool(res["camino"])
        fila = {
            "algoritmo": alg, "existe_ruta": existe, "camino": res["camino"],
            "costo": res["costo"] if existe else None,
            "nodos_visitados": res["nodos_visitados"], "orden_visita": res["orden_visita"],
            "atascado": res.get("atascado", False), **met,
        }
        comparativa.append(fila)
        if principal is None:
            principal, traza_principal = fila, res["traza"]

    resultado = {**principal, "comparativa": [{k: v for k, v in f.items() if k != "orden_visita"} for f in comparativa]}
    return ContratoRespuesta(
        modulo="rutas", operacion=f"buscar_{principal['algoritmo']}", entrada=req.model_dump(),
        resultado=resultado, traza=traza_principal,
        visualizacion={**vis_base, "camino": principal["camino"], "orden_visita": principal["orden_visita"],
                       "caminos_por_algoritmo": {f["algoritmo"]: f["camino"] for f in comparativa}},
        metricas={"tiempo_ms": principal["tiempo_ms"], "memoria_kb": principal["memoria_kb"]},
    )
