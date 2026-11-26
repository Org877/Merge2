from fastapi import APIRouter
from backend.schemas import ContratoRespuesta, VarillasRequest
from backend.core.varillas import ejecutar_corte_varillas

router = APIRouter(prefix="/api/varillas", tags=["Módulo 4: Corte de Varillas"])


@router.post("/resolver", response_model=ContratoRespuesta)
def resolver_varillas(req: VarillasRequest):
    salida = ejecutar_corte_varillas(
        longitud=req.longitud,
        precios=req.precios,
        incluir_recursivo=req.incluir_recursivo,
        limite_recursivo=req.limite_recursivo,
    )
    return ContratoRespuesta(
        modulo="varillas",
        operacion="corte_varillas",
        entrada=req.model_dump(),
        resultado=salida["resultado"],
        traza=salida["traza"],
        visualizacion=salida["visualizacion"],
        metricas=salida["metricas"],
    )