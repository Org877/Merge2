from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field, model_validator


class ContratoRespuesta(BaseModel):
    modulo: str = Field(..., description="Módulo de origen: lenguajes | rutas | complejidad | varillas | probabilistas")
    operacion: str = Field(..., description="Nombre específico de la operación realizada")
    entrada: Dict[str, Any] = Field(..., description="Parámetros de entrada proporcionados por el usuario")
    resultado: Dict[str, Any] = Field(..., description="Resultados estructurados del cómputo")
    traza: List[Dict[str, Any]] = Field(default_factory=list, description="Paso a paso de la ejecución")
    visualizacion: Dict[str, Any] = Field(default_factory=dict, description="Datos preparados para renderizado gráfico")
    metricas: Dict[str, float] = Field(
        default_factory=lambda: {"tiempo_ms": 0.0, "memoria_kb": 0.0},
        description="Mide tiempo (ms) y memoria (KB)",
    )


# Esquemas Módulo 1: Lenguajes, Autómatas y Regex
class LenguajeRequest(BaseModel):
    L: List[str] = Field(default_factory=list)
    M: List[str] = Field(default_factory=list)
    sigma: List[str] = Field(default_factory=list)
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


class RegexRequest(BaseModel):
    regex: str = Field(..., min_length=1, max_length=120, description="Expresión regular (soporta |, *, +, ?, (), concatenación y ε)")
    palabra: str = Field(default="", max_length=200, description="Cadena a probar en el AFD generado")


# Esquemas Módulo 2: Rutas y Grafos
class GrafoRequest(BaseModel):
    grafo: Dict[str, List[Tuple[str, float]]]  # nodo -> [(vecino, peso)]
    origen: str
    destino: str = ""
    dirigido: bool = True
    algoritmos: List[str] = Field(default_factory=lambda: ["star", "dijkstra"])
    heuristica: Optional[Dict[str, float]] = None
    reinicios: int = 0  # Para Hill-Climbing
    modo: str = "ruta"  # "ruta" | "alcance"


# Esquemas Módulo 3: Complejidad y Auditoría AST
class BenchmarkRequest(BaseModel):
    algoritmos: List[str] = Field(default_factory=lambda: ["insertion_sort", "merge_sort"])
    datos_personalizados: Optional[List[int]] = None
    tamano: int = 1000
    tamanos_serie: Optional[List[int]] = None
    semilla: int = 42
    timeout_segundos: float = 5.0
    incluir_series: bool = False


class AuditoriaCodigoRequest(BaseModel):
    codigo: str = Field(..., min_length=1, max_length=10000, description="Código Python a auditar estáticamente con ast")


# Esquemas Módulo 4: Corte de Varillas
class VarillasRequest(BaseModel):
    longitud: int = Field(..., ge=1, le=500, description="Longitud total de la varilla (1 a 500)")
    precios: List[int] = Field(..., min_length=1, description="Precio para cada longitud 1..n")
    incluir_recursivo: bool = Field(default=True, description="Ejecutar comparación contra recursión O(2^n)")
    limite_recursivo: int = Field(default=20, ge=1, le=24, description="Tope seguro para evitar congelamiento exponencial")

    @model_validator(mode="after")
    def validar_precios(self):
        if len(self.precios) < self.longitud:
            raise ValueError(
                f"Se requieren al menos {self.longitud} precios (se recibieron {len(self.precios)})."
            )
        if any(p < 0 for p in self.precios):
            raise ValueError("Todos los precios deben ser mayores o iguales a 0.")
        return self


# Esquemas Módulo 5: Algoritmos Probabilistas
class ProbabilistasRequest(BaseModel):
    numero: int = Field(default=104729, ge=2, le=10**12, description="Entero a evaluar con Miller-Rabin")
    rondas_k: int = Field(default=6, ge=1, le=40, description="Número de rondas k de Miller-Rabin")
    tamano_arreglo: int = Field(default=2000, ge=10, le=50000, description="Tamaño del arreglo para Quicksort Aleatorizado")
    ejecuciones_las_vegas: int = Field(default=5, ge=1, le=20, description="Corridas de Quicksort para medir variabilidad")
    semilla: int = Field(default=42, description="Semilla para reproducibilidad")