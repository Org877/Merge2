from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.schemas import ContratoRespuesta

app = FastAPI(
    title="Plataforma Educativa de Computación",
    version="4.1.0",
    description="Backend oficial con Cómputo Determinista (Fase 1)"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/estado")
def estado_servidor():
    return {"estado": "activo", "motor": "FastAPI", "version": "4.1.0"}

# Aquí se montarán los routers de lenguajes, rutas y complejidad.