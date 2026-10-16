def generar_plantilla(modulo: str, operacion: str, resultado: dict) -> str:
    """Genera una explicación de respaldo basada en plantillas seguras."""
    if modulo == "lenguajes":
        if "afd" in operacion or "afnd" in operacion:
            pertenece = resultado.get("pertenece", False)
            estado = "ACEPTADA" if pertenece else "RECHAZADA"
            return f"**Análisis de Autómata**: La palabra evaluada ha sido **{estado}** por el sistema. El recorrido muestra las transiciones paso a paso de acuerdo con el alfabeto y las reglas definidas."
        else:
            return f"**Operación de Lenguajes ({operacion})**: Se aplicó la operación formal sobre los conjuntos de entrada, generando el lenguaje resultante bajo las reglas de la teoría de autómatas."
            
    elif modulo == "rutas":
        camino = resultado.get("camino", [])
        costo = resultado.get("costo", 0)
        nodos = resultado.get("nodos_visitados", 0)
        camino_str = " -> ".join(camino) if camino else "Sin ruta posible"
        return f"**Optimización de Logística**: Se exploraron {nodos} nodos en total. El camino óptimo encontrado es `{camino_str}` con un costo o distancia acumulada de **{costo}**."
        
    elif modulo == "complejidad":
        algoritmo = resultado.get("algoritmo", "desconocido")
        metricas = resultado.get("metricas", {})
        return f"**Auditoría de Complejidad**: El algoritmo `{algoritmo}` procesó el conjunto de datos en {metricas.get('tiempo_ms', 0)} ms con un consumo pico de memoria de {metricas.get('memoria_kb', 0)} KB."
        
    return "Proceso computacional completado con éxito bajo las restricciones del modelo determinista."