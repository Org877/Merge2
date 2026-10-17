"""Medición de tiempo y memoria. tracemalloc es global al proceso, por eso se serializa con un candado."""
import threading
import time
import tracemalloc

_candado = threading.Lock()


def medir(funcion, *args, **kwargs):
    """Ejecuta funcion(*args) y devuelve (resultado, {"tiempo_ms", "memoria_kb"})."""
    with _candado:
        tracemalloc.start()
        t0 = time.perf_counter()
        try:
            res = funcion(*args, **kwargs)
        finally:
            t1 = time.perf_counter()
            _, pico = tracemalloc.get_traced_memory()
            tracemalloc.stop()
    return res, {"tiempo_ms": round((t1 - t0) * 1000, 4), "memoria_kb": round(pico / 1024, 2)}
