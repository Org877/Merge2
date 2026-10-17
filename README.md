# Plataforma interactiva: Lenguajes, Grafos y Complejidad

Arquitectura en tres capas:

1. **Cómputo determinista (backend):** FastAPI. Única fuente de verdad de los resultados.
2. **Interpretación y explicabilidad:** LLM local con Ollama. No calcula nada, solo explica resultados ya calculados. Si Ollama no está disponible, usa plantillas de respaldo.
3. **Interfaz gráfica (frontend):** HTML + JavaScript (Bootstrap, Cytoscape.js y Chart.js), servida por el mismo FastAPI.

## Requisitos
- Windows 10/11, Python 3.11 o superior.
- (Opcional, recomendado) Ollama, para las explicaciones con LLM. Hardware objetivo: RTX 5070 con 8 GB de VRAM.
(Es el equipo donde lo corrimos)

## Instalación y ejecución (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn backend.main:app --reload
```
- Aplicación: http://127.0.0.1:8000
- Documentación interactiva de la API: http://127.0.0.1:8000/docs

Las librerías JavaScript ya están en `frontend/vendor/`, así que no se necesita internet para usar la app.

## Explicador con LLM local (Ollama)
1. Instala la **última versión de Ollama para Windows** y actualiza el driver NVIDIA (las GPU serie RTX 50 lo requieren).
2. Descarga el modelo: `ollama pull qwen2.5:7b` (~4.7 GB, cabe completo en 8 GB de VRAM).
3. Comprueba con `ollama ps` que el modelo corre al 100 % en GPU.

Configuración (variables de entorno, antes de iniciar uvicorn):
```powershell
$env:OLLAMA_MODEL = "qwen2.5:3b"          # modelo más ligero (por defecto qwen2.5:7b)
$env:OLLAMA_URL   = "http://localhost:11434"
```
Parámetros usados en cada petición: `num_ctx=4096`, `temperature=0.25`, `num_predict=600`, `keep_alive=10m`. La traza se resume a ~30 pasos y solo se inyecta la ficha teórica del tema relevante.

Comportamiento:
- La insignia superior indica el estado: *Ollama activo (modelo, GPU)*, *falta descargar el modelo* u *Ollama apagado: usando plantillas*.
- La explicación se muestra con **streaming** (SSE). Si Ollama falla, se reemplaza automáticamente por la plantilla, de modo que siempre hay texto.
- Se solicita **después** de terminar el cómputo, para no distorsionar las mediciones de tiempo.
- Con el botón **Regenerar explicación** se vuelve a pedir la del último resultado.

## Uso de la interfaz
**1. Lenguajes y Autómatas**
- *Operaciones con lenguajes:* unión, intersección, diferencia, concatenación, potencia L^k, clausura positiva, complemento (hasta longitud k) e inversa.
- *Análisis de una cadena:* longitud, inversa, conteo de símbolos, prefijos y sufijos.
- *Autómatas (AFD, AFND, AFND-ε):* transiciones una por línea como `origen,símbolo,destino` (usa `eps` para ε). Se dibuja el autómata (aceptación con doble círculo, flecha de inicio) y se anima el recorrido con Anterior / Siguiente / Reproducir, con veredicto ACEPTADA o RECHAZADA.

**2. Rutas y Grafos**
- Aristas una por línea como `origen,destino,peso`; grafo dirigido o no dirigido.
- Algoritmos: Dijkstra, A*, Greedy, BFS, DFS y Hill-Climbing (con reinicios). Se pueden marcar varios para compararlos sobre el mismo grafo; el primero marcado es el que se dibuja.
- Heurística opcional como `A:6, B:5, E:0`. A*, Greedy y Hill-Climbing la usan; Hill-Climbing la exige.
- Modo **alcance máximo**: todos los nodos alcanzables desde el origen con su distancia en saltos.
- La ruta hallada se resalta con línea roja gruesa, borde marcado y ★ en el destino. El botón *Animar orden de visita* numera los nodos en el orden explorado.
- Tabla comparativa: camino, costo, nodos visitados, tiempo y memoria.

**3. Complejidad y Benchmark**
- Catálogo: Insertion Sort y Merge Sort (P), Subset-Sum y TSP por fuerza bruta (NP), Reachability con Savitch (NSPACE). Mínimo 2 algoritmos.
- Datos aleatorios con tamaño y semilla. Opción de curva de crecimiento tiempo vs. tamaño y escala logarítmica.
- Protecciones: tamaño máximo de 5000, límites para los exponenciales (Subset-Sum 16, TSP 10, Reachability 10) y timeout configurable. Si se excede, se avisa en pantalla (`abortado`) en lugar de colgar el servidor.
- Los algoritmos se ejecutan en secuencia y con candado, para no mezclar las mediciones de `tracemalloc`.

## Estructura del proyecto
```
proyecto/
├── backend/
│   ├── main.py                 app FastAPI, CORS, routers y archivos estáticos
│   ├── schemas.py              contrato de respuesta y modelos de entrada
│   ├── core/
│   │   ├── automatas.py        lenguajes, cadenas, AFD / AFND / AFND-ε
│   │   ├── grafos.py           BFS, DFS, Dijkstra, A*, Greedy, Hill-Climbing, alcance
│   │   ├── complejidad.py      catálogo y algoritmos P / NP / NSPACE
│   │   └── medicion.py         tiempo y memoria (con candado)
│   └── routers/                lenguajes.py, rutas.py, complejidad.py, explicar.py
├── explicador/
│   ├── cliente_ollama.py       cliente httpx asíncrono (estado, generar, stream)
│   ├── servicio.py             arma el prompt, elige la ficha, fallback
│   ├── prompts.py              prompt del sistema y resumen de traza
│   ├── plantillas.py           explicaciones de respaldo sin LLM
│   └── fichas/*.md             fichas teóricas por tema
├── frontend/
│   ├── index.html, css/styles.css
│   ├── js/api.js, js/app.js
│   └── vendor/                 bootstrap, cytoscape, chart.js (locales)
├── tests/                      pytest
├── requirements.txt
└── README.md
```

## Contrato de respuesta
Todos los endpoints de cómputo devuelven la misma forma, que consumen el explicador y el frontend:
```json
{
  "modulo": "lenguajes | rutas | complejidad",
  "operacion": "simular_afd",
  "entrada": {},
  "resultado": {},
  "traza": [{"paso": 1, "descripcion": "..."}],
  "visualizacion": {},
  "metricas": {"tiempo_ms": 0.0, "memoria_kb": 0.0}
}
```

## Endpoints
| Método | Ruta | Uso |
|---|---|---|
| GET | `/api/estado` | estado del servidor |
| POST | `/api/lenguajes/operacion?op=union` | operaciones con lenguajes |
| POST | `/api/lenguajes/cadena` | análisis de una cadena |
| POST | `/api/lenguajes/automata` | AFD / AFND / AFND-ε (`transiciones`: `{estado: {símbolo: [destinos]}}`, ε = `"eps"`) |
| POST | `/api/rutas/buscar` | búsqueda de ruta (varios algoritmos) o alcance (`"modo": "alcance"`) |
| GET | `/api/complejidad/catalogo` | catálogo con clase y complejidad teórica |
| POST | `/api/complejidad/benchmark` | benchmark, con `incluir_series` para la curva de crecimiento |
| GET | `/api/explicar/estado` | estado de Ollama, modelo y GPU |
| POST | `/api/explicar` | explicación completa |
| POST | `/api/explicar/stream` | explicación por streaming (SSE) |

Los errores de validación devuelven mensajes en español en el campo `detail`, y la interfaz los muestra en una alerta.

## Pruebas
```powershell
python -m pytest -q
```
Cubren los tres módulos (casos válidos y de error), el servicio de archivos estáticos y el fallback del explicador cuando Ollama no está activo.
