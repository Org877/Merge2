document.addEventListener("DOMContentLoaded", () => {
    verificarEstadoOllamaFrontend();

    // Módulo 1: Operaciones de Lenguajes
    document.getElementById("btn-ejecutar-m1").addEventListener("click", async () => {
        const L = document.getElementById("m1-L").value.split(",").map(s => s.trim()).filter(s => s);
        const M = document.getElementById("m1-M").value.split(",").map(s => s.trim()).filter(s => s);
        const op = document.getElementById("m1-op-tipo").value;
        const k = parseInt(document.getElementById("m1-k").value) || 2;

        const payload = { L, M, sigma: ["a", "b"], k };
        const data = await apiPost(`/api/lenguajes/operacion?op=${op}`, payload);

        if (data) {
            document.getElementById("m1-viz").innerHTML = `
                <h6>Resultado de ${op.toUpperCase()}:</h6>
                <p class="font-monospace text-success">${JSON.stringify(data.resultado.resultado)}</p>
                <small class="text-muted">Tiempo: ${data.metricas.tiempo_ms} ms</small>
            `;
            solicitarExplicacion(data);
        }
    });

    // Módulo 2: Rutas y Grafos
    document.getElementById("btn-ejecutar-m2").addEventListener("click", async () => {
        const algoritmo = document.getElementById("m2-algoritmo").value;
        const origen = document.getElementById("m2-origen").value;
        const destino = document.getElementById("m2-destino").value;

        // Grafo de prueba predeterminado
        const grafo = {
            "A": [["B", 2.0], ["C", 5.0]],
            "B": [["C", 1.0], ["D", 4.0]],
            "C": [["D", 2.0]],
            "D": []
        };

        const payload = { grafo, origen, destino, dirigido: true, algoritmos: [algoritmo] };
        const data = await apiPost(`/api/rutas/buscar`, payload);

        if (data) {
            document.getElementById("m2-grafo-container").innerHTML = `
                <div class="p-3">
                    <h6>Camino Óptimo (${algoritmo.toUpperCase()}):</h6>
                    <p class="fw-bold text-primary">${data.resultado.camino.join(" ➔ ")}</p>
                    <p><strong>Costo Total:</strong> ${data.resultado.costo}</p>
                    <small>Nodos visitados: ${data.resultado.nodos_visitados} | Tiempo: ${data.metricas.tiempo_ms} ms</small>
                </div>
            `;
            solicitarExplicacion(data);
        }
    });

    // Módulo 3: Benchmark
    document.getElementById("btn-ejecutar-m3").addEventListener("click", async () => {
        const tamano = parseInt(document.getElementById("m3-tamano").value) || 1000;
        const payload = { algoritmos: ["insertion_sort", "merge_sort"], tamano };
        const data = await apiPost(`/api/complejidad/benchmark`, payload);

        if (data) {
            document.getElementById("panel-explicacion").innerText = "Benchmark completado con éxito. Revise las métricas de rendimiento.";
            document.getElementById("fuente-explicacion").innerText = "Datos deterministas";
        }
    });
});

async function solicitarExplicacion(contratoJson) {
    const data = await apiPost(`/api/explicar`, contratoJson);
    if (data) {
        document.getElementById("panel-explicacion").innerHTML = marked ? marked.parse(data.explicacion) : data.explicacion;
        document.getElementById("fuente-explicacion").innerText = `Fuente: ${data.fuente.toUpperCase()}`;
    }
}