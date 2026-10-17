SYSTEM_PROMPT = """Eres un tutor experto, amigable y riguroso especializado en ciencias de la computación, diseñado específicamente para estudiantes de nuevo ingreso.
Tu objetivo es interpretar y explicar los resultados técnicos proporcionados en formato JSON de manera clara, pedagógica y estrictamente en español.

Estructura obligatoria de tu respuesta:
1. **Qué se hizo**: Resumen directo de la tarea ejecutada.
2. **Cómo se obtuvo (Paso a paso)**: Explicación lógica apoyada en la traza de ejecución provista.
3. **Base teórica**: Fundamento conceptual breve sustentado en la ficha técnica de referencia.
4. **Significado de las métricas**: Interpretación sencilla del tiempo de ejecución y el uso de memoria.

REGLAS CRÍTICAS:
- No inventes datos, costos, rutas o estados que no estén explícitamente en el resultado o la traza.
- Si falta información o no hay ruta, comunícalo con absoluta honestidad pedagógica."""

def _hoja(x, limite=400):
    """Recorta valores largos para que el prompt quepa en num_ctx=4096."""
    s = str(x)
    return s if len(s) <= limite else s[:limite] + "…"


def resumir_traza(traza: list, maximo: int = 30) -> list:
    if len(traza) <= maximo:
        return traza
    mitad = maximo // 2
    return traza[:mitad] + [{"descripcion": f"... ({len(traza) - maximo} pasos omitidos) ..."}] + traza[-mitad:]


def construir_prompt(contrato: dict, ficha: str) -> str:
    import json
    res = contrato.get("resultado", {})
    res = {k: (v if k != "comparativa" else [{kk: vv for kk, vv in f.items() if kk != "orden_visita"} for f in v])
           for k, v in res.items()}
    partes = [
        f"MÓDULO: {contrato.get('modulo')}\nOPERACIÓN: {contrato.get('operacion')}",
        f"ENTRADA: {_hoja(json.dumps(contrato.get('entrada', {}), ensure_ascii=False), 700)}",
        f"RESULTADO: {_hoja(json.dumps(res, ensure_ascii=False), 1400)}",
        f"TRAZA: {_hoja(json.dumps(resumir_traza(contrato.get('traza', [])), ensure_ascii=False), 1400)}",
        f"MÉTRICAS: {json.dumps(contrato.get('metricas', {}))}",
        f"FICHA TEÓRICA DE REFERENCIA:\n{ficha}",
        "Explica este resultado siguiendo la estructura obligatoria.",
    ]
    return "\n\n".join(partes)
