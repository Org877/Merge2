from typing import Any, Dict

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from explicador import cliente_ollama, servicio

router = APIRouter(prefix="/api/explicar", tags=["Capa 2: Explicador (LLM local)"])


@router.get("/estado")
async def estado():
    return await cliente_ollama.estado()


@router.post("")
async def explicar(contrato: Dict[str, Any]):
    return await servicio.explicar(contrato)


@router.post("/stream")
async def explicar_stream(contrato: Dict[str, Any]):
    return StreamingResponse(servicio.explicar_stream(contrato), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
