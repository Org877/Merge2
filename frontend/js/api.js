// Mismo origen que el backend (FastAPI sirve el frontend). Si abres el HTML con otro servidor, cambia API_BASE.
const API_BASE = "";

function mostrarError(msg) {
    const a = document.getElementById("alerta");
    a.textContent = msg;
    a.classList.remove("d-none");
    clearTimeout(mostrarError._t);
    mostrarError._t = setTimeout(() => a.classList.add("d-none"), 9000);
}
function limpiarError() { document.getElementById("alerta").classList.add("d-none"); }

async function apiPost(endpoint, data) {
    limpiarError();
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            let msg = "Error en la solicitud al servidor.";
            try {
                const err = await response.json();
                if (typeof err.detail === "string") msg = err.detail;
                else if (Array.isArray(err.detail))
                    msg = "Revisa los datos de entrada: " + err.detail.map(d => `${(d.loc || []).slice(1).join(".")}: ${d.msg}`).join("; ");
            } catch (_) { /* respuesta sin JSON */ }
            mostrarError(msg);
            return null;
        }
        return await response.json();
    } catch (error) {
        console.error("API Error:", error);
        mostrarError("No se pudo conectar con el servidor. ¿Está corriendo uvicorn?");
        return null;
    }
}

async function verificarEstadoOllamaFrontend() {
    const badge = document.getElementById("estado-ollama");
    try {
        const res = await fetch(`${API_BASE}/api/explicar/estado`);
        const data = await res.json();
        if (data.activo && data.modelo_disponible) {
            badge.className = "badge bg-success";
            badge.textContent = `Ollama activo (${data.modelo}${data.en_gpu ? ", GPU" : ""})`;
        } else {
            badge.className = "badge bg-secondary";
            badge.textContent = data.activo ? `Falta descargar ${data.modelo}: usando plantillas` : "Ollama apagado: usando plantillas";
        }
    } catch (e) {
        badge.className = "badge bg-danger";
        badge.textContent = "Backend desconectado";
    }
}
