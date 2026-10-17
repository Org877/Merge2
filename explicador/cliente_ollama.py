"""Cliente asíncrono para Ollama (local). El modelo se configura con OLLAMA_MODEL."""
import json
import os
from typing import AsyncIterator

import httpx

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODELO = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
TIMEOUT = httpx.Timeout(connect=2.0, read=120.0, write=10.0, pool=5.0)

OPCIONES = {"num_ctx": 4096, "temperature": 0.25, "num_predict": 600}
KEEP_ALIVE = "10m"


async def estado() -> dict:
    info = {"activo": False, "modelo": MODELO, "modelo_disponible": False, "en_gpu": False}
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(2.0)) as c:
            tags = (await c.get(f"{OLLAMA_URL}/api/tags")).json()
            info["activo"] = True
            nombres = {m.get("name", "") for m in tags.get("models", [])}
            info["modelo_disponible"] = MODELO in nombres or f"{MODELO}:latest" in nombres
            ps = (await c.get(f"{OLLAMA_URL}/api/ps")).json()
            for m in ps.get("models", []):
                if m.get("name") == MODELO and m.get("size_vram", 0) >= 0.95 * m.get("size", 1):
                    info["en_gpu"] = True
    except Exception:
        pass
    return info


def _payload(system: str, prompt: str, stream: bool) -> dict:
    return {"model": MODELO, "system": system, "prompt": prompt, "stream": stream,
            "options": OPCIONES, "keep_alive": KEEP_ALIVE}


async def generar(system: str, prompt: str) -> str:
    async with httpx.AsyncClient(timeout=TIMEOUT) as c:
        r = await c.post(f"{OLLAMA_URL}/api/generate", json=_payload(system, prompt, False))
        r.raise_for_status()
        return r.json()["response"].strip()


async def generar_stream(system: str, prompt: str) -> AsyncIterator[str]:
    async with httpx.AsyncClient(timeout=TIMEOUT) as c:
        async with c.stream("POST", f"{OLLAMA_URL}/api/generate", json=_payload(system, prompt, True)) as r:
            r.raise_for_status()
            async for linea in r.aiter_lines():
                if not linea:
                    continue
                datos = json.loads(linea)
                if datos.get("response"):
                    yield datos["response"]
                if datos.get("done"):
                    break
