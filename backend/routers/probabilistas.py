from fastapi import APIRouter
from backend.schemas import ContratoRespuesta, ProbabilistasRequest
from backend.core.probabilistas import ejecutar_benchmark_probabilistas

router = APIRouter(prefix="/api/probabilistas", tags=["Módulo 5: Probabilistas"])


@router.post("/benchmark", response_model=ContratoRespuesta)
def benchmark_probabilistas(req: ProbabilistasRequest):
    salida = ejecutar_benchmark_probabilistas(
        numero=req.numero,
        rondas_k=req.rondas_k,
        tamano_arreglo=req.tamano_arreglo,
        ejecuciones_las_vegas=req.ejecuciones_las_vegas,
        semilla=req.semilla,
    )
    return ContratoRespuesta(
        modulo="probabilistas",
        operacion="benchmark_probabilistas",
        entrada=req.model_dump(),
        resultado=salida["resultado"],
        traza=salida["traza"],
        visualizacion=salida["visualizacion"],
        metricas=salida["metricas"],
    )