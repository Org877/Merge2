import json
from pathlib import Path
from typing import AsyncIterator

from explicador import cliente_ollama
from explicador.plantillas import generar_plantilla
from explicador.prompts import SYSTEM_PROMPT, construir_prompt

FICHAS = Path(__file__).parent / "fichas"


def tema_de(contrato: dict) -> str:
    modulo, op = contrato.get("modulo", ""), contrato.get("operacion", "")
    if modulo == "lenguajes":
        if op == "regex_a_afd":
            return "regex"
        if op.startswith("simular_"):
            return {"afd": "afd", "afnd": "afnd", "afnde": "afnd_epsilon"}.get(op.split("_", 1)[1], "afd")
        return "lenguajes"
    if modulo == "rutas":
        return "alcance" if op == "alcance_maximo" else {"star": "astar"}.get(op.replace("buscar_", ""), op.replace("buscar_", ""))
    if modulo == "complejidad":
        return "auditoria_ast" if op == "auditar_ast" else "complejidad"
    if modulo == "varillas":
        return "varillas"
    if modulo == "probabilistas":
        return "probabilistas"
    return "lenguajes"


def cargar_ficha(tema: str) -> str:
    f = FICHAS / f"{tema}.md"
    return f.read_text(encoding="utf-8") if f.exists() else "(sin ficha disponible)"


def plantilla(contrato: dict) -> str:
    return generar_plantilla(contrato.get("modulo", ""), contrato.get("operacion", ""),
                             contrato.get("resultado", {}), contrato.get("metricas"))


async def explicar(contrato: dict) -> dict:
    prompt = construir_prompt(contrato, cargar_ficha(tema_de(contrato)))
    try:
        texto = await cliente_ollama.generar(SYSTEM_PROMPT, prompt)
        if texto:
            return {"explicacion": texto, "fuente": "llm"}
    except Exception:
        pass
    return {"explicacion": plantilla(contrato), "fuente": "plantilla"}


async def explicar_stream(contrato: dict) -> AsyncIterator[str]:
    """Genera eventos SSE: {"token": ...} y al final {"fin": true, "fuente": ...}."""
    def ev(d): return f"data: {json.dumps(d, ensure_ascii=False)}\n\n"
    prompt = construir_prompt(contrato, cargar_ficha(tema_de(contrato)))
    emitio = False
    try:
        async for tok in cliente_ollama.generar_stream(SYSTEM_PROMPT, prompt):
            emitio = True
            yield ev({"token": tok})
        if emitio:
            yield ev({"fin": True, "fuente": "llm"})
            return
    except Exception:
        pass
    # Falla de Ollama: si ya se emitió texto parcial lo conservamos; si no, plantilla completa.
    if emitio:
        yield ev({"fin": True, "fuente": "llm"})
    else:
        yield ev({"reemplazar": plantilla(contrato)})
        yield ev({"fin": True, "fuente": "plantilla"})
