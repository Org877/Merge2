const API_BASE = "http://127.0.0.1:8000";

async function apiPost(endpoint, data) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error("Error en la solicitud al servidor.");
        return await response.json();
    } catch (error) {
        console.error("API Error:", error);
        return null;
    }
}

async function verificarEstadoOllamaFrontend() {
    try {
        const res = await fetch(`${API_BASE}/api/explicar/estado`);
        const data = await res.json();
        const badge = document.getElementById("estado-ollama");
        if (data.activo && data.modelo_disponible) {
            badge.className = "badge bg-success";
            badge.innerText = "Ollama Activo (GPU RTX 5070)";
        } else {
            badge.className = "badge bg-secondary";
            badge.innerText = "Usando Plantillas de Respaldo";
        }
    } catch (e) {
        document.getElementById("estado-ollama").className = "badge bg-danger";
        document.getElementById("estado-ollama").innerText = "Backend Desconectado";
    }
}