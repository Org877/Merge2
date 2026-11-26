from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.routers import complejidad, explicar, lenguajes, probabilistas, rutas, varillas

app = FastAPI(
    title="Plataforma Educativa de Computación",
    version="5.0.0",
    description="Autómatas/Regex, rutas en grafos, complejidad/AST, corte de varillas y probabilistas, con explicador LLM local.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/estado")
def estado_servidor():
    return {"estado": "activo", "motor": "FastAPI", "version": "5.0.0"}


app.include_router(lenguajes.router)
app.include_router(rutas.router)
app.include_router(complejidad.router)
app.include_router(varillas.router)
app.include_router(probabilistas.router)
app.include_router(explicar.router)

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")