/* Lógica de UI para Regex->AFN-e->AFD, Auditoría AST, Módulo 4 (Varillas) y Módulo 5 (Probabilistas). */

let _ultimoContratoExtra = null;
window._ultimoFueExtra = false;

let _cyRegex = null;
let _datosRegexActual = null;
let _vistaRegex = "afd";
let _pasoRegex = 0;
let _timerRegex = null;

let _chartVarillas = null;
let _chartErrorMC = null;
let _chartTiempoLV = null;

function _escaparHtml(str) {
    return String(str ?? "").replace(/[&<>"']/g, m => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m]));
}

function _renderMarkdownBasico(texto) {
    return _escaparHtml(texto)
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/`([^`]+)`/g, "<code>$1</code>")
        .replace(/\n/g, "<br>");
}

async function pedirExplicacionExtra(contrato) {
    _ultimoContratoExtra = contrato;
    window._ultimoFueExtra = true;

    const panel = document.getElementById("panel-explicacion");
    const badge = document.getElementById("fuente-explicacion");
    const btnReg = document.getElementById("btn-regenerar");
    if (btnReg) btnReg.disabled = false;

    panel.innerHTML = `<div class="d-flex align-items-center gap-2 text-muted"><div class="spinner-border spinner-border-sm"></div><span>Generando explicación...</span></div>`;
    badge.className = "badge bg-warning text-dark";
    badge.textContent = "Fuente: generando...";

    let acumulado = "";
    try {
        const resp = await fetch(`${API_BASE}/api/explicar/stream`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(contrato),
        });
        if (!resp.ok || !resp.body) throw new Error("Fallo en streaming");

        const reader = resp.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            const partes = buffer.split("\n\n");
            buffer = partes.pop();

            for (const bloque of partes) {
                const linea = bloque.trim();
                if (!linea.startsWith("data:")) continue;
                const ev = JSON.parse(linea.slice(5).trim());
                if (ev.token) {
                    acumulado += ev.token;
                    panel.innerHTML = _renderMarkdownBasico(acumulado);
                } else if (ev.reemplazar) {
                    acumulado = ev.reemplazar;
                    panel.innerHTML = _renderMarkdownBasico(acumulado);
                } else if (ev.fin) {
                    const esLLM = ev.fuente === "llm";
                    badge.className = esLLM ? "badge bg-success" : "badge bg-secondary";
                    badge.textContent = esLLM ? "Fuente: LLM local (Ollama)" : "Fuente: Plantilla determinista (fallback)";
                    verificarEstadoOllamaFrontend();
                }
            }
        }
    } catch (_) {
        const res = await apiPost("/api/explicar", contrato);
        if (res) {
            panel.innerHTML = _renderMarkdownBasico(res.explicacion || "");
            badge.className = res.fuente === "llm" ? "badge bg-success" : "badge bg-secondary";
            badge.textContent = res.fuente === "llm" ? "Fuente: LLM local (Ollama)" : "Fuente: Plantilla determinista (fallback)";
            verificarEstadoOllamaFrontend();
        }
    }
}

/* ==================== 1. REGEX -> AFN-e -> AFD ==================== */
function _dibujarAutomataRegex() {
    if (!_datosRegexActual) return;
    const viz = _datosRegexActual.visualizacion;
    const grafo = _vistaRegex === "afd" ? { nodos: viz.nodos, aristas: viz.aristas } : viz.afn_epsilon;

    const elements = [];
    for (const n of grafo.nodos) {
        const clases = [];
        if (n.inicial) clases.push("inicial");
        if (n.aceptacion) clases.push("aceptacion");
        elements.push({ data: { id: n.id, label: n.inicial ? `→ ${n.id}` : n.id }, classes: clases.join(" ") });
    }
    grafo.aristas.forEach((a, i) => {
        elements.push({ data: { id: `e${i}`, source: a.origen, target: a.destino, label: a.simbolo } });
    });

    if (_cyRegex) _cyRegex.destroy();
    _cyRegex = cytoscape({
        container: document.getElementById("m1-regex-cy"),
        elements,
        style: [
            {
                selector: "node",
                style: {
                    "label": "data(label)",
                    "text-valign": "center",
                    "text-halign": "center",
                    "background-color": "#f8f9fa",
                    "border-width": 2,
                    "border-color": "#212529",
                    "width": 44,
                    "height": 44,
                    "font-size": 12
                }
            },
            { selector: "node.inicial", style: { "border-color": "#0d6efd", "border-width": 3 } },
            { selector: "node.aceptacion", style: { "border-style": "double", "border-width": 5, "border-color": "#198754" } },
            { selector: "node.activo", style: { "background-color": "#ffc107", "border-color": "#dc3545", "border-width": 4 } },
            {
                selector: "edge",
                style: {
                    "label": "data(label)",
                    "curve-style": "bezier",
                    "target-arrow-shape": "triangle",
                    "line-color": "#6c757d",
                    "target-arrow-color": "#6c757d",
                    "font-size": 12,
                    "text-background-color": "#ffffff",
                    "text-background-opacity": 0.85
                }
            }
        ],
        layout: { name: "breadthfirst", directed: true, padding: 24, spacingFactor: 1.3 }
    });
    _actualizarPasoRegex();
}

function _actualizarPasoRegex() {
    if (!_datosRegexActual || !_cyRegex) return;
    _cyRegex.nodes().removeClass("activo");
    const pasoLabel = document.getElementById("m1-regex-paso");
    if (_vistaRegex !== "afd") {
        pasoLabel.textContent = "Mostrando AFN-ε (cambia a AFD para animar la simulación).";
        return;
    }
    const rec = _datosRegexActual.visualizacion.recorrido || [];
    if (!rec.length) return;
    _pasoRegex = Math.max(0, Math.min(_pasoRegex, rec.length - 1));
    for (const id of rec[_pasoRegex]) {
        _cyRegex.getElementById(id).addClass("activo");
    }
    const palabra = _datosRegexActual.resultado.palabra || "";
    const prefijo = palabra.slice(0, _pasoRegex);
    pasoLabel.textContent = `Paso ${_pasoRegex}/${rec.length - 1} · Estado: ${rec[_pasoRegex].join(", ")} · Leído: "${prefijo}"`;
}

async function ejecutarRegex() {
    clearInterval(_timerRegex);
    const regex = document.getElementById("m1-regex-expr").value.trim();
    const palabra = document.getElementById("m1-regex-palabra").value;
    const data = await apiPost("/api/lenguajes/regex", { regex, palabra });
    if (!data) return;

    _datosRegexActual = data;
    _vistaRegex = "afd";
    _pasoRegex = 0;

    document.getElementById("btn-ver-afd").classList.add("active", "btn-dark");
    document.getElementById("btn-ver-afd").classList.remove("btn-outline-dark");
    document.getElementById("btn-ver-afne").classList.remove("active", "btn-dark");
    document.getElementById("btn-ver-afne").classList.add("btn-outline-dark");

    const r = data.resultado;
    const ver = document.getElementById("m1-regex-veredicto");
    ver.textContent = r.veredicto;
    ver.className = `badge fs-6 ${r.aceptada ? "bg-success" : "bg-danger"}`;

    document.getElementById("m1-regex-resumen").innerHTML = `
        <div class="border rounded p-2 bg-light">
            <div><strong>Postfija:</strong> <code>${_escaparHtml(r.postfija)}</code></div>
            <div><strong>AFN-ε:</strong> ${r.resumen_afn_epsilon.num_estados} estados → <strong>AFD:</strong> ${r.afd.num_estados} estados</div>
            <div><strong>Aceptación AFD:</strong> ${r.afd.estados_aceptacion.join(", ") || "ninguno"}</div>
            <div><strong>Métricas:</strong> ${data.metricas.tiempo_ms} ms · ${data.metricas.memoria_kb} KB</div>
        </div>`;

    _dibujarAutomataRegex();
    pedirExplicacionExtra(data);
}

/* ==================== 2. AUDITORÍA AST (MÓDULO 3) ==================== */
async function ejecutarAuditoriaAST() {
    const codigo = document.getElementById("m3-ast-codigo").value;
    const data = await apiPost("/api/complejidad/auditar", { codigo });
    if (!data) return;

    const r = data.resultado;
    const filasBucles = r.bucles.map(b =>
        `<tr><td>${b.linea}</td><td><code>${b.tipo}</code></td><td>${b.profundidad}</td><td><code>${_escaparHtml(b.funcion)}</code></td></tr>`
    ).join("") || `<tr><td colspan="4" class="text-muted text-center">Sin bucles detectados</td></tr>`;

    const recTxt = r.funciones_recursivas.length
        ? r.funciones_recursivas.map(f => `<code>${_escaparHtml(f.funcion)}</code> (línea ${f.linea}, ${f.llamadas_internas} llamada(s))`).join(", ")
        : "Ninguna";

    document.getElementById("m3-ast-resultado").innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-2">
            <span class="badge bg-primary fs-6">${_escaparHtml(r.complejidad_estimada)}</span>
            <span class="small text-muted">${data.metricas.tiempo_ms} ms · ${data.metricas.memoria_kb} KB</span>
        </div>
        <div class="small mb-2">
            <strong>Profundidad máx. de bucles:</strong> ${r.profundidad_max_bucles} ·
            <strong>Total bucles:</strong> ${r.total_bucles} ·
            <strong>Nodos AST:</strong> ${r.nodos_ast_analizados}<br>
            <strong>Recursión:</strong> ${recTxt}
        </div>
        <table class="table table-sm table-bordered mb-0 bg-white">
            <thead><tr><th>Línea</th><th>Estructura</th><th>Profundidad</th><th>Función</th></tr></thead>
            <tbody>${filasBucles}</tbody>
        </table>`;

    pedirExplicacionExtra(data);
}

/* ==================== 3. MÓDULO 4: CORTE DE VARILLAS ==================== */
async function ejecutarVarillas() {
    const longitud = parseInt(document.getElementById("m4-longitud").value, 10);
    const precios = document.getElementById("m4-precios").value
        .split(",")
        .map(s => s.trim())
        .filter(Boolean)
        .map(Number);

    if (precios.some(Number.isNaN)) {
        mostrarError("La lista de precios debe contener únicamente números separados por comas.");
        return;
    }

    const payload = {
        longitud,
        precios,
        incluir_recursivo: document.getElementById("m4-incluir-rec").checked,
        limite_recursivo: parseInt(document.getElementById("m4-limite-rec").value, 10) || 20,
    };

    const data = await apiPost("/api/varillas/resolver", payload);
    if (!data) return;

    const r = data.resultado;
    const rec = r.recursion;
    let recCard = "";
    if (rec.estado === "completado") {
        recCard = `<strong>${rec.metricas.tiempo_ms} ms</strong> · ${rec.metricas.memoria_kb} KB<br><span class="small text-muted">${rec.llamadas.toLocaleString()} llamadas recursivas</span>`;
    } else if (rec.estado === "omitido_por_limite") {
        recCard = `<span class="text-danger small">${_escaparHtml(rec.motivo)}</span>`;
    } else {
        recCard = `<span class="text-muted small">Desactivado</span>`;
    }

    document.getElementById("m4-resumen").innerHTML = `
        <div class="row g-2">
            <div class="col-md-4"><div class="border rounded p-2 bg-light h-100">
                <div class="small text-muted">Ingreso máximo (n=${r.longitud})</div>
                <div class="fs-4 fw-bold text-success">$${r.ingreso_maximo}</div>
                <div class="small">Cortes exactos: <code>[${r.cortes_optimos.join(" + ")}]</code></div>
            </div></div>
            <div class="col-md-4"><div class="border rounded p-2 bg-light h-100">
                <div class="small text-muted">Tabulación O(n²)</div>
                <div><strong>${r.tabulacion.metricas.tiempo_ms} ms</strong> · ${r.tabulacion.metricas.memoria_kb} KB</div>
                <div class="small text-muted">${r.tabulacion.operaciones} operaciones</div>
            </div></div>
            <div class="col-md-4"><div class="border rounded p-2 bg-light h-100">
                <div class="small text-muted">Recursión O(2ⁿ)</div>
                <div>${recCard}</div>
            </div></div>
        </div>`;

    const curva = data.visualizacion.curva_crecimiento;
    if (_chartVarillas) _chartVarillas.destroy();
    _chartVarillas = new Chart(document.getElementById("m4-chart"), {
        type: "line",
        data: {
            labels: curva.tamanos.map(t => `n=${t}`),
            datasets: [
                { label: "Tabulación O(n²) [ms]", data: curva.tabulacion_ms, borderColor: "#198754", tension: 0.2 },
                { label: "Recursión O(2ⁿ) [ms]", data: curva.recursion_ms, borderColor: "#dc3545", tension: 0.2 }
            ]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    const filas = data.visualizacion.tabla_dp.slice(0, 25).map(x =>
        `<tr><td>${x.longitud}</td><td>${x.ingreso}</td><td>${x.corte}</td></tr>`
    ).join("");
    document.getElementById("m4-tabla").innerHTML = `
        <table class="table table-sm table-striped table-bordered">
            <thead><tr><th>Longitud j</th><th>Ingreso óptimo dp[j]</th><th>Primer corte óptimo</th></tr></thead>
            <tbody>${filas}</tbody>
        </table>`;

    pedirExplicacionExtra(data);
}

/* ==================== 4. MÓDULO 5: PROBABILISTAS ==================== */
async function ejecutarProbabilistas() {
    const payload = {
        numero: parseInt(document.getElementById("m5-numero").value, 10),
        rondas_k: parseInt(document.getElementById("m5-rondas").value, 10),
        tamano_arreglo: parseInt(document.getElementById("m5-tamano").value, 10),
        ejecuciones_las_vegas: parseInt(document.getElementById("m5-ejecuciones").value, 10),
        semilla: parseInt(document.getElementById("m5-semilla").value, 10) || 42,
    };

    const data = await apiPost("/api/probabilistas/benchmark", payload);
    if (!data) return;

    const mc = data.resultado.monte_carlo_miller_rabin;
    const lv = data.resultado.las_vegas_quicksort;

    document.getElementById("m5-resumen").innerHTML = `
        <div class="row g-2">
            <div class="col-md-6"><div class="border rounded p-3 bg-light h-100">
                <div class="d-flex justify-content-between">
                    <strong>Miller-Rabin (Monte Carlo)</strong>
                    <span class="badge ${mc.veredicto === "COMPUESTO" ? "bg-danger" : "bg-success"}">${mc.veredicto}</span>
                </div>
                <div class="small mt-1">
                    n = <code>${mc.numero}</code> · Rondas ejecutadas: ${mc.rondas_ejecutadas}/${mc.rondas_k}<br>
                    Cota error teórico (4⁻ᵏ): <code>${mc.cota_error_teorica.toExponential(2)}</code>${mc.testigo ? ` · Testigo: <code>${mc.testigo}</code>` : ""}<br>
                    Métricas: <strong>${mc.metricas.tiempo_ms} ms</strong> · ${mc.metricas.memoria_kb} KB
                </div>
            </div></div>
            <div class="col-md-6"><div class="border rounded p-3 bg-light h-100">
                <div class="d-flex justify-content-between">
                    <strong>Quicksort Aleatorizado (Las Vegas)</strong>
                    <span class="badge ${lv.todas_exactas ? "bg-success" : "bg-danger"}">${lv.todas_exactas ? "100% EXACTO" : "ERROR"}</span>
                </div>
                <div class="small mt-1">
                    Arreglo n = ${lv.tamano_arreglo} · Corridas: ${lv.ejecuciones} · Tasa de error: <strong>0%</strong><br>
                    Tiempo prom.: <strong>${lv.tiempo_promedio_ms} ms</strong> (min ${lv.tiempo_min_ms} / max ${lv.tiempo_max_ms} ms)<br>
                    Memoria prom.: ${lv.memoria_promedio_kb} KB
                </div>
            </div></div>
        </div>`;

    const ce = data.visualizacion.curva_error_monte_carlo;
    if (_chartErrorMC) _chartErrorMC.destroy();
    _chartErrorMC = new Chart(document.getElementById("m5-chart-error"), {
        type: "line",
        data: {
            labels: ce.rondas.map(r => `k=${r}`),
            datasets: [
                { label: "Cota teórica 4⁻ᵏ", data: ce.cota_teorica_4_menos_k, borderColor: "#0d6efd", tension: 0.2 },
                { label: "Error empírico (n=561)", data: ce.error_empirico_carmichael_561, borderColor: "#dc3545", tension: 0.2 }
            ]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    const tlv = data.visualizacion.tiempos_las_vegas;
    if (_chartTiempoLV) _chartTiempoLV.destroy();
    _chartTiempoLV = new Chart(document.getElementById("m5-chart-lv"), {
        type: "bar",
        data: {
            labels: tlv.etiquetas,
            datasets: [{ label: "Tiempo Las Vegas (ms)", data: tlv.tiempos_ms, backgroundColor: "#198754" }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    const filasLV = lv.corridas.map(c =>
        `<tr><td>#${c.corrida}</td><td>${c.exacto ? "✅ Exacto" : "❌"}</td><td>${c.comparaciones.toLocaleString()}</td><td>${c.pivotes_elegidos.toLocaleString()}</td><td>${c.tiempo_ms} ms</td><td>${c.memoria_kb} KB</td></tr>`
    ).join("");
    document.getElementById("m5-tabla-lv").innerHTML = `
        <table class="table table-sm table-bordered">
            <thead><tr><th>Corrida</th><th>Exactitud</th><th>Comparaciones</th><th>Pivotes</th><th>Tiempo</th><th>Memoria</th></tr></thead>
            <tbody>${filasLV}</tbody>
        </table>`;

    pedirExplicacionExtra(data);
}

/* ==================== EVENTOS ==================== */
document.addEventListener("DOMContentLoaded", () => {
    // Coordinación limpia del botón Regenerar con app.js
    ["btn-ejecutar-m1", "btn-ejecutar-m2", "btn-ejecutar-m3"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener("click", () => { window._ultimoFueExtra = false; }, true);
    });
    const btnReg = document.getElementById("btn-regenerar");
    if (btnReg) {
        btnReg.addEventListener("click", (e) => {
            if (window._ultimoFueExtra && _ultimoContratoExtra) {
                e.stopImmediatePropagation();
                pedirExplicacionExtra(_ultimoContratoExtra);
            }
        }, true);
    }

    // Módulo 1: Regex
    document.getElementById("btn-ejecutar-regex")?.addEventListener("click", ejecutarRegex);
    document.getElementById("btn-ejemplo-regex")?.addEventListener("click", () => {
        document.getElementById("m1-regex-expr").value = "(a|b)*abb";
        document.getElementById("m1-regex-palabra").value = "ababb";
    });
    document.getElementById("btn-ver-afd")?.addEventListener("click", () => {
        _vistaRegex = "afd";
        document.getElementById("btn-ver-afd").classList.replace("btn-outline-dark", "btn-dark");
        document.getElementById("btn-ver-afne").classList.replace("btn-dark", "btn-outline-dark");
        _dibujarAutomataRegex();
    });
    document.getElementById("btn-ver-afne")?.addEventListener("click", () => {
        _vistaRegex = "afne";
        document.getElementById("btn-ver-afne").classList.replace("btn-outline-dark", "btn-dark");
        document.getElementById("btn-ver-afd").classList.replace("btn-dark", "btn-outline-dark");
        _dibujarAutomataRegex();
    });
    document.getElementById("m1-regex-prev")?.addEventListener("click", () => { clearInterval(_timerRegex); _pasoRegex--; _actualizarPasoRegex(); });
    document.getElementById("m1-regex-next")?.addEventListener("click", () => { clearInterval(_timerRegex); _pasoRegex++; _actualizarPasoRegex(); });
    document.getElementById("m1-regex-play")?.addEventListener("click", () => {
        clearInterval(_timerRegex);
        _pasoRegex = 0;
        _actualizarPasoRegex();
        const total = (_datosRegexActual?.visualizacion?.recorrido || []).length;
        _timerRegex = setInterval(() => {
            if (_pasoRegex + 1 >= total) { clearInterval(_timerRegex); return; }
            _pasoRegex++;
            _actualizarPasoRegex();
        }, 700);
    });

    // Módulo 3: AST
    document.getElementById("btn-auditar-ast")?.addEventListener("click", ejecutarAuditoriaAST);
    document.getElementById("btn-ejemplo-ast")?.addEventListener("click", () => {
        document.getElementById("m3-ast-codigo").value =
`def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)`;
    });

    // Módulo 4: Varillas
    document.getElementById("btn-ejecutar-m4")?.addEventListener("click", ejecutarVarillas);
    document.getElementById("btn-ejemplo-m4")?.addEventListener("click", () => {
        document.getElementById("m4-longitud").value = "14";
        document.getElementById("m4-precios").value = "1, 5, 8, 9, 10, 17, 17, 20, 24, 30, 32, 35, 39, 42";
    });

    // Módulo 5: Probabilistas
    document.getElementById("btn-ejecutar-m5")?.addEventListener("click", ejecutarProbabilistas);
    document.getElementById("btn-ejemplo-primo")?.addEventListener("click", () => {
        document.getElementById("m5-numero").value = "104729";
        document.getElementById("m5-rondas").value = "6";
    });
    document.getElementById("btn-ejemplo-carmichael")?.addEventListener("click", () => {
        document.getElementById("m5-numero").value = "561";
        document.getElementById("m5-rondas").value = "5";
    });
});