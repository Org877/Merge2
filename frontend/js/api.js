// Mismo origen que el backend (FastAPI sirve el frontend).
const API_BASE = "";
let _peticionesActivas = 0;

function mostrarSpinner(mostrar, texto = "Procesando cálculo determinista...") {
    const el = document.getElementById("spinner-global");
    const txt = document.getElementById("spinner-texto");
    if (!el) return;
    if (mostrar) {
        _peticionesActivas++;
        if (txt) txt.textContent = texto;
        el.classList.remove("d-none");
    } else {
        _peticionesActivas = Math.max(0, _peticionesActivas - 1);
        if (_peticionesActivas === 0) el.classList.add("d-none");
    }
}

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
    mostrarSpinner(true);
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
    } finally {
        mostrarSpinner(false);
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