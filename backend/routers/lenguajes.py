from fastapi import APIRouter, HTTPException

from backend.core.automatas import analizar_cadena, operar_lenguajes, simular_automata
from backend.core.medicion import medir
from backend.core.regex_engine import convertir_y_simular_regex
from backend.schemas import AutomataRequest, ContratoRespuesta, LenguajeRequest, RegexRequest

router = APIRouter(prefix="/api/lenguajes", tags=["Módulo 1: Lenguajes"])


@router.post("/operacion", response_model=ContratoRespuesta)
def procesar_lenguaje(req: LenguajeRequest, op: str = "union"):
    try:
        res, met = medir(operar_lenguajes, op, req.L, req.M, req.sigma, req.k)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ContratoRespuesta(
        modulo="lenguajes",
        operacion=op,
        entrada=req.model_dump(),
        resultado={"resultado": res},
        metricas=met,
    )


@router.post("/cadena", response_model=ContratoRespuesta)
def procesar_cadena(req: LenguajeRequest):
    res, met = medir(analizar_cadena, req.palabra or "")
    return ContratoRespuesta(
        modulo="lenguajes",
        operacion="analizar_cadena",
        entrada=req.model_dump(),
        resultado=res,
        metricas=met,
    )


def _agrupar_aristas(req: AutomataRequest):
    """Agrupa los símbolos de una misma transición origen->destino (ej. 'a,b') y marca ε."""
    grupos = {}
    for origen, trans in req.transiciones.items():
        for simbolo, destinos in trans.items():
            etiqueta = "ε" if simbolo in ("eps", "ε") else simbolo
            for d in destinos:
                grupos.setdefault((origen, d), []).append(etiqueta)
    return [
        {"origen": o, "destino": d, "simbolo": ",".join(sorted(sims))}
        for (o, d), sims in grupos.items()
    ]


@router.post("/automata", response_model=ContratoRespuesta)
def procesar_automata(req: AutomataRequest):
    try:
        res, met = medir(simular_automata, req)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    bruto = res.get("recorrido_estados") or res.get("recorrido") or []
    recorrido = [x if isinstance(x, list) else [x] for x in bruto]
    return ContratoRespuesta(
        modulo="lenguajes",
        operacion=f"simular_{req.tipo}",
        entrada=req.model_dump(),
        resultado=res,
        traza=res.get("traza", []),
        visualizacion={
            "nodos": [
                {"id": e, "inicial": e == req.estado_inicial, "aceptacion": e in req.estados_aceptacion}
                for e in req.estados
            ],
            "aristas": _agrupar_aristas(req),
            "recorrido": recorrido,
        },
        metricas=met,
    )


@router.post("/regex", response_model=ContratoRespuesta)
def procesar_regex(req: RegexRequest):
    try:
        salida, met = medir(convertir_y_simular_regex, req.regex, req.palabra)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ContratoRespuesta(
        modulo="lenguajes",
        operacion="regex_a_afd",
        entrada=req.model_dump(),
        resultado=salida["resultado"],
        traza=salida["traza"],
        visualizacion=salida["visualizacion"],
        metricas=met,
    )