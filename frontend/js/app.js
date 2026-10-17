/* ===================== utilidades ===================== */
const $ = (id) => document.getElementById(id);
const csv = (txt) => txt.split(",").map(s => s.trim()).filter(Boolean);
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

async function conCarga(btn, fn) {
    const txt = btn.textContent;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Procesando...';
    try { await fn(); } finally { btn.disabled = false; btn.textContent = txt; }
}

// Markdown mínimo (negritas, código, listas) sin dependencias externas.
function mdLigero(texto) {
    let h = esc(texto);
    h = h.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/`([^`]+)`/g, "<code>$1</code>");
    h = h.replace(/^\s*[-*] (.+)$/gm, "<li>$1</li>").replace(/(<li>.*<\/li>\n?)+/g, (m) => `<ul>${m}</ul>`);
    return h.replace(/\n{2,}/g, "<br><br>").replace(/\n/g, "<br>");
}

/* ===================== explicador (streaming SSE) ===================== */
let ultimoContrato = null;

async function solicitarExplicacion(contrato) {
    ultimoContrato = contrato;
    $("btn-regenerar").disabled = false;
    const panel = $("panel-explicacion"), fuente = $("fuente-explicacion");
    panel.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Generando explicación...';
    fuente.textContent = "Fuente: ...";
    let texto = "", origen = "plantilla";
    try {
        const resp = await fetch(`${API_BASE}/api/explicar/stream`, {
            method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(contrato)
        });
        if (!resp.ok || !resp.body) throw new Error("sin stream");
        const lector = resp.body.getReader(), dec = new TextDecoder();
        let buf = "";
        while (true) {
            const { done, value } = await lector.read();
            if (done) break;
            buf += dec.decode(value, { stream: true });
            const eventos = buf.split("\n\n");
            buf = eventos.pop();
            for (const e of eventos) {
                if (!e.startsWith("data: ")) continue;
                const d = JSON.parse(e.slice(6));
                if (d.token) { texto += d.token; panel.innerHTML = mdLigero(texto); }
                if (d.reemplazar) { texto = d.reemplazar; panel.innerHTML = mdLigero(texto); }
                if (d.fin) origen = d.fuente;
            }
        }
    } catch (e) {
        const data = await apiPost("/api/explicar", contrato);
        if (data) { texto = data.explicacion; origen = data.fuente; panel.innerHTML = mdLigero(texto); }
    }
    fuente.textContent = `Fuente: ${origen === "llm" ? "LLM local" : "plantilla de respaldo"}`;
}
$("btn-regenerar").addEventListener("click", () => ultimoContrato && solicitarExplicacion(ultimoContrato));

/* ===================== estilos Cytoscape ===================== */
const ESTILO_CY = [
    { selector: "node", style: { label: "data(label)", "text-valign": "center", "text-halign": "center",
        "background-color": "#fff", "border-width": 2, "border-color": "#333", width: 46, height: 46, "font-size": 13 } },
    { selector: "node.aceptacion", style: { "border-style": "double", "border-width": 7 } },
    { selector: "node.inicio", style: { width: 2, height: 2, "border-width": 0, label: "", "background-opacity": 0 } },
    { selector: "node.activo", style: { "background-color": "#ffc107", "border-color": "#d63384", "border-width": 5 } },
    { selector: "node.visitado", style: { "background-color": "#cfe2ff" } },
    { selector: "node.alcanzable", style: { "background-color": "#d1e7dd" } },
    { selector: "node.camino", style: { "border-color": "#dc3545", "border-width": 6 } },
    { selector: "edge", style: { width: 2, "line-color": "#6c757d", "target-arrow-color": "#6c757d",
        "target-arrow-shape": "triangle", "curve-style": "bezier", label: "data(label)", "font-size": 12,
        "text-background-color": "#fff", "text-background-opacity": 1, "text-background-padding": 2,
        "text-rotation": "autorotate" } },
    { selector: "edge.sin-flecha", style: { "target-arrow-shape": "none" } },
    { selector: "edge.camino", style: { width: 6, "line-color": "#dc3545", "target-arrow-color": "#dc3545" } },
];

function crearCy(contenedor, elementos, layout) {
    return cytoscape({ container: contenedor, elements: elementos, style: ESTILO_CY,
        layout: layout || { name: "cose", animate: false, idealEdgeLength: 120, nodeRepulsion: 9000, padding: 30 } });
}

/* ===================== MÓDULO 1 ===================== */
let cy1 = null, pasos1 = [], idx1 = 0, timer1 = null, verdicto1 = null;

$("m1-tarea").addEventListener("change", () => {
    const t = $("m1-tarea").value;
    $("m1-form-op").classList.toggle("d-none", t !== "operacion");
    $("m1-form-cadena").classList.toggle("d-none", t !== "cadena");
    $("m1-form-auto").classList.toggle("d-none", t !== "automata");
    $("m1-cy-wrap").classList.add("d-none");
});

const EJEMPLOS_AUTO = {
    afd: { estados: "q0, q1", alfabeto: "a, b", inicial: "q0", acept: "q0", trans: "q0,a,q1\nq0,b,q0\nq1,a,q0\nq1,b,q1", palabra: "abba" },
    afnd: { estados: "q0, q1, q2", alfabeto: "a, b", inicial: "q0", acept: "q2", trans: "q0,a,q0\nq0,b,q0\nq0,b,q1\nq1,b,q2", palabra: "abb" },
    afnde: { estados: "q0, q1, q2", alfabeto: "a, b", inicial: "q0", acept: "q2", trans: "q0,eps,q1\nq1,a,q1\nq1,b,q2\nq2,eps,q0", palabra: "aab" },
};
$("m1-tipo-auto").addEventListener("change", () => $("btn-ejemplo-m1").click());
$("btn-ejemplo-m1").addEventListener("click", () => {
    if ($("m1-tarea").value !== "automata") return;
    const e = EJEMPLOS_AUTO[$("m1-tipo-auto").value];
    $("m1-estados").value = e.estados; $("m1-alfabeto").value = e.alfabeto; $("m1-inicial").value = e.inicial;
    $("m1-acept").value = e.acept; $("m1-trans").value = e.trans; $("m1-palabra").value = e.palabra;
});

function parseTransiciones(txt) {
    const t = {};
    for (const linea of txt.split("\n").map(l => l.trim()).filter(Boolean)) {
        const [o, s, d] = linea.split(",").map(x => x.trim());
        if (!o || !s || !d) throw new Error(`Transición mal escrita: "${linea}". Usa origen,símbolo,destino.`);
        const sim = (s === "ε") ? "eps" : s;
        ((t[o] = t[o] || {})[sim] = t[o][sim] || []).push(d);
    }
    return t;
}

function mostrarPaso1(i) {
    if (!cy1) return;
    idx1 = Math.max(0, Math.min(i, pasos1.length - 1));
    cy1.nodes().removeClass("activo");
    (pasos1[idx1] || []).forEach(id => cy1.getElementById(id).addClass("activo"));
    $("m1-paso").textContent = `Paso ${idx1} de ${pasos1.length - 1}: activos {${(pasos1[idx1] || []).join(", ")}}`;
    const v = $("m1-veredicto");
    if (idx1 === pasos1.length - 1 && verdicto1 !== null) {
        v.className = "ms-auto badge fs-6 " + (verdicto1 ? "bg-success" : "bg-danger");
        v.textContent = verdicto1 ? "✔ ACEPTADA" : "✘ RECHAZADA";
    } else { v.className = "ms-auto badge fs-6"; v.textContent = ""; }
}
$("m1-prev").addEventListener("click", () => { clearInterval(timer1); mostrarPaso1(idx1 - 1); });
$("m1-next").addEventListener("click", () => { clearInterval(timer1); mostrarPaso1(idx1 + 1); });
$("m1-play").addEventListener("click", () => {
    clearInterval(timer1); mostrarPaso1(0);
    timer1 = setInterval(() => { if (idx1 >= pasos1.length - 1) clearInterval(timer1); else mostrarPaso1(idx1 + 1); }, 800);
});

function dibujarAutomata(v) {
    $("m1-cy-wrap").classList.remove("d-none");
    const els = [{ data: { id: "__ini" }, classes: "inicio" }];
    v.nodos.forEach(n => {
        els.push({ data: { id: n.id, label: n.id }, classes: n.aceptacion ? "aceptacion" : "" });
        if (n.inicial) els.push({ data: { id: "e_ini", source: "__ini", target: n.id, label: "inicio" } });
    });
    v.aristas.forEach((a, i) => els.push({ data: { id: `e${i}`, source: a.origen, target: a.destino, label: a.simbolo } }));
    cy1 = crearCy($("m1-cy"), els, { name: "circle", padding: 40 });
    pasos1 = v.recorrido || [];
    mostrarPaso1(0);
}

$("btn-ejecutar-m1").addEventListener("click", (ev) => conCarga(ev.currentTarget, async () => {
    const tarea = $("m1-tarea").value;
    let data = null;
    clearInterval(timer1);
    if (tarea === "operacion") {
        const op = $("m1-op-tipo").value;
        const payload = { L: csv($("m1-L").value), M: csv($("m1-M").value), sigma: csv($("m1-sigma").value), k: parseInt($("m1-k").value) || 0 };
        data = await apiPost(`/api/lenguajes/operacion?op=${op}`, payload);
        if (data) {
            const r = data.resultado.resultado;
            $("m1-cy-wrap").classList.add("d-none");
            $("m1-viz").innerHTML = `<h6>Resultado de ${esc(op)} (${r.length} cadena${r.length === 1 ? "" : "s"}):</h6>` +
                (r.length ? r.map(x => `<span class="badge bg-primary font-monospace me-1 mb-1">${x === "" ? "ε" : esc(x)}</span>`).join("") : "<em>conjunto vacío ∅</em>") +
                `<div class="small text-muted mt-2">Tiempo: ${data.metricas.tiempo_ms} ms</div>`;
        }
    } else if (tarea === "cadena") {
        data = await apiPost("/api/lenguajes/cadena", { palabra: $("m1-w").value });
        if (data) {
            const r = data.resultado;
            $("m1-cy-wrap").classList.add("d-none");
            $("m1-viz").innerHTML = `<table class="table table-sm mb-0"><tbody>
                <tr><th>Longitud</th><td>${r.longitud}</td></tr>
                <tr><th>Inversa</th><td class="font-monospace">${esc(r.inversa) || "ε"}</td></tr>
                <tr><th>Conteo de símbolos</th><td class="font-monospace">${esc(JSON.stringify(r.conteo_simbolos))}</td></tr>
                <tr><th>Prefijos</th><td class="font-monospace">${r.prefijos.map(p => esc(p) || "ε").join(", ")}</td></tr>
                <tr><th>Sufijos</th><td class="font-monospace">${r.sufijos.map(p => esc(p) || "ε").join(", ")}</td></tr></tbody></table>`;
        }
    } else {
        let transiciones;
        try { transiciones = parseTransiciones($("m1-trans").value); } catch (e) { mostrarError(e.message); return; }
        const payload = { tipo: $("m1-tipo-auto").value, estados: csv($("m1-estados").value), alfabeto: csv($("m1-alfabeto").value),
            transiciones, estado_inicial: $("m1-inicial").value.trim(), estados_aceptacion: csv($("m1-acept").value), palabra: $("m1-palabra").value };
        data = await apiPost("/api/lenguajes/automata", payload);
        if (data) {
            verdicto1 = !!data.resultado.pertenece;
            const motivo = data.resultado.motivo ? `<div class="text-danger small">${esc(data.resultado.motivo)}</div>` : "";
            $("m1-viz").innerHTML = `<h6>Palabra <code>${esc(payload.palabra) || "ε"}</code>: ` +
                `<span class="badge ${verdicto1 ? "bg-success" : "bg-danger"}">${verdicto1 ? "ACEPTADA" : "RECHAZADA"}</span></h6>${motivo}` +
                `<ol class="small mb-0">${data.traza.map(t => `<li>${esc(t.descripcion)}</li>`).join("")}</ol>`;
            dibujarAutomata(data.visualizacion);
        }
    }
    if (data) solicitarExplicacion(data);
}));

/* ===================== MÓDULO 2 ===================== */
let cy2 = null, ultimaViz2 = null, timer2 = null;

$("btn-ejemplo-m2").addEventListener("click", () => {
    $("m2-aristas").value = "A,B,2\nA,C,5\nB,C,1\nB,D,4\nC,D,2\nD,E,3\nC,E,6";
    $("m2-origen").value = "A"; $("m2-destino").value = "E"; $("m2-heur").value = "A:6, B:5, C:3, D:3, E:0";
});

function parseAristas(txt) {
    const grafo = {};
    for (const linea of txt.split("\n").map(l => l.trim()).filter(Boolean)) {
        const p = linea.split(/[,;\s]+/);
        if (p.length < 2) throw new Error(`Arista mal escrita: "${linea}". Usa origen,destino,peso.`);
        const peso = p[2] === undefined ? 1 : parseFloat(p[2]);
        if (Number.isNaN(peso)) throw new Error(`El peso de "${linea}" no es un número.`);
        (grafo[p[0]] = grafo[p[0]] || []).push([p[1], peso]);
        grafo[p[1]] = grafo[p[1]] || [];
    }
    return grafo;
}
function parseHeur(txt) {
    const h = {};
    csv(txt).forEach(par => { const [k, v] = par.split(":").map(s => s.trim()); if (k && !Number.isNaN(parseFloat(v))) h[k] = parseFloat(v); });
    return Object.keys(h).length ? h : null;
}

function dibujarGrafo(v) {
    const els = v.nodos.map(n => ({ data: { id: n, label: n } }));
    v.aristas.forEach((a, i) => els.push({ data: { id: `a${i}`, source: a.origen, target: a.destino, label: String(a.peso) }, classes: v.dirigido ? "" : "sin-flecha" }));
    cy2 = crearCy($("m2-grafo-container"), els);
    // Ruta hallada: borde rojo grueso + estrella en la etiqueta (no depende solo del color).
    const cam = v.camino || [];
    cam.forEach((n, i) => {
        const nodo = cy2.getElementById(n);
        nodo.addClass("camino");
        nodo.data("label", `${n}${i === 0 ? " (inicio)" : ""}${i === cam.length - 1 ? " ★" : ""}`);
        if (i > 0) cy2.edges().filter(e => {
            const s = e.data("source"), t = e.data("target"), u = cam[i - 1];
            return (s === u && t === n) || (!v.dirigido && s === n && t === u);
        }).addClass("camino");
    });
    if (v.alcanzables) Object.entries(v.alcanzables).forEach(([n, d]) => {
        const nodo = cy2.getElementById(n); nodo.addClass("alcanzable"); nodo.data("label", `${n} (${d})`);
    });
}

$("m2-animar").addEventListener("click", () => {
    if (!cy2 || !ultimaViz2) return;
    clearInterval(timer2);
    cy2.nodes().removeClass("visitado");
    const orden = ultimaViz2.orden_visita || []; let i = 0;
    timer2 = setInterval(() => {
        if (i >= orden.length) { clearInterval(timer2); return; }
        const nodo = cy2.getElementById(orden[i]);
        nodo.addClass("visitado");
        const base = nodo.data("label").replace(/ #\d+$/, "");
        nodo.data("label", `${base} #${i + 1}`);
        i++;
    }, 600);
});

function tablaRutas(comp) {
    $("m2-tabla").innerHTML = `<table class="table table-sm table-striped"><thead><tr>
        <th>Algoritmo</th><th>Camino</th><th>Costo</th><th>Nodos</th><th>Tiempo (ms)</th><th>Memoria (KB)</th></tr></thead><tbody>` +
        comp.map(c => `<tr><td>${esc(c.algoritmo)}</td><td>${c.existe_ruta ? esc(c.camino.join(" → ")) : (c.atascado ? "<em>atascado (mínimo local)</em>" : "<em>sin ruta</em>")}</td>
        <td>${c.costo ?? "—"}</td><td>${c.nodos_visitados}</td><td>${c.tiempo_ms}</td><td>${c.memoria_kb}</td></tr>`).join("") + "</tbody></table>";
}

$("btn-ejecutar-m2").addEventListener("click", (ev) => conCarga(ev.currentTarget, async () => {
    let grafo;
    try { grafo = parseAristas($("m2-aristas").value); } catch (e) { mostrarError(e.message); return; }
    const alcance = $("m2-alcance").checked;
    const algoritmos = [...document.querySelectorAll(".m2-alg:checked")].map(x => x.value);
    const payload = { grafo, origen: $("m2-origen").value.trim(), destino: $("m2-destino").value.trim(),
        dirigido: $("m2-dirigido").checked, algoritmos, heuristica: parseHeur($("m2-heur").value),
        reinicios: parseInt($("m2-reinicios").value) || 0, modo: alcance ? "alcance" : "ruta" };
    const data = await apiPost("/api/rutas/buscar", payload);
    if (!data) return;
    clearInterval(timer2);
    ultimaViz2 = data.visualizacion;
    dibujarGrafo(data.visualizacion);
    if (alcance) {
        const r = data.resultado;
        $("m2-tabla").innerHTML = `<div class="alert alert-success">Alcanzables desde <b>${esc(payload.origen)}</b>: ` +
            Object.entries(r.alcanzables).map(([k, v]) => `${esc(k)} (${v} saltos)`).join(", ") +
            `.<br>No alcanzables: ${r.no_alcanzables.length ? esc(r.no_alcanzables.join(", ")) : "ninguno"}.</div>`;
    } else tablaRutas(data.resultado.comparativa);
    solicitarExplicacion(data);
}));

/* ===================== MÓDULO 3 ===================== */
let chBarras = null, chSerie = null;
const COLORES_CLASE = { P: "#198754", NP: "#dc3545", NSPACE: "#0dcaf0" };
const PALETA = ["#0d6efd", "#dc3545", "#198754", "#fd7e14", "#6f42c1"];

$("btn-ejemplo-m3").addEventListener("click", () => {
    document.querySelectorAll(".m3-alg").forEach(c => c.checked = ["insertion_sort", "merge_sort", "subset_sum"].includes(c.value));
    $("m3-tamano").value = 1000; $("m3-semilla").value = 42;
});

function dibujarGraficas(vis, log) {
    const tipoY = log ? "logarithmic" : "linear";
    if (chBarras) chBarras.destroy();
    chBarras = new Chart($("m3-chart-barras"), {
        type: "bar",
        data: { labels: vis.barras.map(b => `${b.algoritmo} [${b.clase}]`),
            datasets: [{ label: "Tiempo (ms)", data: vis.barras.map(b => Math.max(b.tiempo_ms, 0.001)), backgroundColor: vis.barras.map(b => COLORES_CLASE[b.clase] || "#6c757d") }] },
        options: { maintainAspectRatio: false, scales: { y: { type: tipoY, title: { display: true, text: "ms" } } }, plugins: { legend: { display: false } } }
    });
    if (chSerie) { chSerie.destroy(); chSerie = null; }
    if (vis.series.length) {
        chSerie = new Chart($("m3-chart-serie"), {
            type: "line",
            data: { datasets: vis.series.map((s, i) => ({ label: `${s.algoritmo} [${s.clase}]`, borderColor: PALETA[i % PALETA.length],
                backgroundColor: PALETA[i % PALETA.length], borderDash: s.clase === "NP" ? [6, 4] : [], pointStyle: ["circle", "rect", "triangle", "rectRot", "star"][i % 5],
                data: s.tamanos.map((t, j) => ({ x: t, y: Math.max(s.tiempos_ms[j], 0.001) })) })) },
            options: { maintainAspectRatio: false, scales: { x: { type: "linear", title: { display: true, text: "tamaño n" } },
                y: { type: tipoY, title: { display: true, text: "ms" } } } }
        });
    }
}

$("btn-ejecutar-m3").addEventListener("click", (ev) => conCarga(ev.currentTarget, async () => {
    const algoritmos = [...document.querySelectorAll(".m3-alg:checked")].map(x => x.value);
    if (algoritmos.length < 2) { mostrarError("Selecciona al menos 2 algoritmos para compararlos."); return; }
    const payload = { algoritmos, tamano: parseInt($("m3-tamano").value) || 1000, semilla: parseInt($("m3-semilla").value) || 42,
        incluir_series: $("m3-series").checked };
    const data = await apiPost("/api/complejidad/benchmark", payload);
    if (!data) return;
    const r = data.resultado;
    $("m3-avisos").innerHTML = r.avisos.map(a => `<div class="alert alert-warning py-1 small">⚠ ${esc(a)}</div>`).join("");
    dibujarGraficas(data.visualizacion, $("m3-log").checked);
    $("m3-tabla").innerHTML = `<table class="table table-sm table-striped"><thead><tr><th>Algoritmo</th><th>Clase</th><th>Complejidad</th>
        <th>Tiempo (ms)</th><th>Memoria (KB)</th><th>Estado</th></tr></thead><tbody>` +
        r.comparativa.map(c => `<tr><td>${esc(c.algoritmo)}</td><td>${esc(c.clase)}</td><td>${esc(c.complejidad)}</td>
        <td>${c.metricas.tiempo_ms}</td><td>${c.metricas.memoria_kb}</td><td>${c.abortado ? "⚠ abortado" : "✔ completo"}</td></tr>`).join("") + "</tbody></table>";
    solicitarExplicacion(data);
}));

document.addEventListener("DOMContentLoaded", verificarEstadoOllamaFrontend);
