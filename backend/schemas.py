from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

class ContratoRespuesta(BaseModel):
    modulo: str = Field(..., description="Módulo de origen: lenguajes | rutas | complejidad")
    operacion: str = Field(..., description="Nombre específico de la operación realizada")
    entrada: Dict[str, Any] = Field(..., description="Parámetros de entrada proporcionados por el usuario")
    resultado: Dict[str, Any] = Field(..., description="Resultados estructurados del cómputo")
    traza: List[Dict[str, Any]] = Field(default=[], description="Paso a paso de la ejecución")
    visualizacion: Dict[str, Any] = Field(default={}, description="Datos preparados para renderizado gráfico")
    metricas: Dict[str, float] = Field(default={"tiempo_ms": 0.0, "memoria_kb": 0.0}, description="Mide tiempo y memoria")

# Esquemas Módulo 1
class LenguajeRequest(BaseModel):
    L: List[str] = []
    M: List[str] = []
    sigma: List[str] = []
    k: int = 0
    palabra: Optional[str] = ""

class AutomataRequest(BaseModel):
    estados: List[str]
    alfabeto: List[str]
    transiciones: Dict[str, Dict[str, List[str]]]  # Soporta AFD, AFND y AFND-e (listas de destinos)
    estado_inicial: str
    estados_aceptacion: List[str]
    palabra: str
    tipo: str = "afd"  # "afd", "afnd", "afnde"

# Esquemas Módulo 2
class GrafoRequest(BaseModel):
    grafo: Dict[str, List[Tuple[str, float]]]  # nodo -> [(vecino, peso)] o lista de aristas
    origen: str
    destino: str = ""
    dirigido: bool = True
    algoritmos: List[str] = ["star", "dijkstra"]
    heuristica: Optional[Dict[str, float]] = None
    reinicios: int = 0  # Para Hill-Climbing
    modo: str = "ruta"  # "ruta" | "alcance" (alcance máximo desde el origen)

# Esquemas Módulo 3
class BenchmarkRequest(BaseModel):
    algoritmos: List[str] = ["insertion_sort", "merge_sort"]
    datos_personalizados: Optional[List[int]] = None
    tamano: int = 1000
    tamanos_serie: Optional[List[int]] = None  # Para curvas de crecimiento
    semilla: int = 42
    timeout_segundos: float = 5.0
    incluir_series: bool = False