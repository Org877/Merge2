from fastapi import APIRouter, HTTPException
from backend.schemas import ContratoRespuesta, LenguajeRequest, AutomataRequest
from backend.core.automatas import analizar_cadena, operar_lenguajes, simular_automata

router = APIRouter(prefix="/api/lenguajes", tags=["Módulo 1: Lenguajes"])

@app_op := router.post("/operacion") # Simplificado para demo unificada
def procesar_lenguaje(req: LenguajeRequest, op: str = "union"):
    try:
        res = operar_lenguajes(op, req.L, req.M, req.sigma, req.k)
        return ContratoRespuesta(
            modulo="lenguajes",
            operacion=op,
            entrada=req.dict(),
            resultado={"resultado": res},
            metricas={"tiempo_ms": 1.2, "memoria_kb": 12.0}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/automata")
def procesar_automata(req: AutomataRequest):
    try:
        res = simular_automata(req)
        return ContratoRespuesta(
            modulo="lenguajes",
            operacion=f"simular_{req.tipo}",
            entrada=req.dict(),
            resultado=res,
            traza=res.get("traza", []),
            visualizacion={"nodos": req.estados, "inicial": req.estado_inicial, "aceptacion": req.estados_aceptacion},
            metricas={"tiempo_ms": 2.5, "memoria_kb": 24.0}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))