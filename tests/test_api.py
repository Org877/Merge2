from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

AFD = {"tipo": "afd", "estados": ["q0", "q1"], "alfabeto": ["a", "b"],
       "transiciones": {"q0": {"a": ["q1"], "b": ["q0"]}, "q1": {"a": ["q0"], "b": ["q1"]}},
       "estado_inicial": "q0", "estados_aceptacion": ["q0"], "palabra": "abba"}
GRAFO = {"A": [["B", 2], ["C", 5]], "B": [["C", 1], ["D", 4]], "C": [["D", 2]], "D": []}


def test_frontend_servido():
    r = client.get("/")
    assert r.status_code == 200 and "Plataforma" in r.text
    assert client.get("/vendor/cytoscape.min.js").status_code == 200


def test_lenguajes_union():
    r = client.post("/api/lenguajes/operacion?op=union", json={"L": ["a", "b"], "M": ["b", "c"]})
    assert r.status_code == 200
    assert r.json()["resultado"]["resultado"] == ["a", "b", "c"]


def test_cadena():
    r = client.post("/api/lenguajes/cadena", json={"palabra": "abc"})
    assert r.json()["resultado"]["inversa"] == "cba"


def test_afd_acepta_y_rechaza():
    r = client.post("/api/lenguajes/automata", json=AFD).json()
    assert r["resultado"]["pertenece"] is True      # dos 'a' -> estado q0
    assert r["visualizacion"]["recorrido"][-1] == ["q0"]
    r = client.post("/api/lenguajes/automata", json={**AFD, "palabra": "a"}).json()
    assert r["resultado"]["pertenece"] is False


def test_afd_simbolo_invalido_da_400_claro():
    r = client.post("/api/lenguajes/automata", json={**AFD, "palabra": "z"})
    assert r.status_code == 400 and "alfabeto" in r.json()["detail"]


def test_afnd_y_afnde():
    afnd = {"tipo": "afnd", "estados": ["q0", "q1", "q2"], "alfabeto": ["a", "b"],
            "transiciones": {"q0": {"a": ["q0"], "b": ["q0", "q1"]}, "q1": {"b": ["q2"]}},
            "estado_inicial": "q0", "estados_aceptacion": ["q2"], "palabra": "abb"}
    assert client.post("/api/lenguajes/automata", json=afnd).json()["resultado"]["pertenece"] is True
    afne = {"tipo": "afnde", "estados": ["q0", "q1", "q2"], "alfabeto": ["a", "b"],
            "transiciones": {"q0": {"eps": ["q1"]}, "q1": {"a": ["q1"], "b": ["q2"]}},
            "estado_inicial": "q0", "estados_aceptacion": ["q2"], "palabra": "aab"}
    assert client.post("/api/lenguajes/automata", json=afne).json()["resultado"]["pertenece"] is True


def test_rutas_todos_los_algoritmos():
    heur = {"A": 4, "B": 3, "C": 2, "D": 0}
    r = client.post("/api/rutas/buscar", json={"grafo": GRAFO, "origen": "A", "destino": "D",
        "algoritmos": ["dijkstra", "star", "greedy", "bfs", "dfs", "hill"], "heuristica": heur}).json()
    comp = {c["algoritmo"]: c for c in r["resultado"]["comparativa"]}
    assert comp["dijkstra"]["costo"] == 5.0 and comp["dijkstra"]["camino"] == ["A", "B", "C", "D"]
    assert comp["star"]["costo"] == 5.0
    assert all(c["existe_ruta"] for c in comp.values())


def test_rutas_sin_camino_y_nodo_inexistente():
    r = client.post("/api/rutas/buscar", json={"grafo": GRAFO, "origen": "D", "destino": "A", "algoritmos": ["bfs"]}).json()
    assert r["resultado"]["existe_ruta"] is False and r["resultado"]["camino"] == []
    r = client.post("/api/rutas/buscar", json={"grafo": GRAFO, "origen": "Z", "destino": "A", "algoritmos": ["bfs"]})
    assert r.status_code == 400


def test_hill_climbing_necesita_heuristica_y_se_atasca():
    r = client.post("/api/rutas/buscar", json={"grafo": GRAFO, "origen": "A", "destino": "D", "algoritmos": ["hill"]})
    assert r.status_code == 400
    trampa = {"A": [["B", 1], ["C", 1]], "B": [], "C": [["D", 1]], "D": []}
    r = client.post("/api/rutas/buscar", json={"grafo": trampa, "origen": "A", "destino": "D",
        "algoritmos": ["hill"], "heuristica": {"A": 5, "B": 1, "C": 9, "D": 0}}).json()
    assert r["resultado"]["atascado"] is True


def test_alcance_maximo():
    r = client.post("/api/rutas/buscar", json={"grafo": GRAFO, "origen": "C", "modo": "alcance"}).json()
    assert r["resultado"]["alcanzables"] == {"C": 0, "D": 1}
    assert r["resultado"]["no_alcanzables"] == ["A", "B"]


def test_benchmark_p_np_nspace():
    r = client.post("/api/complejidad/benchmark", json={"algoritmos": ["insertion_sort", "merge_sort", "subset_sum", "reachability"],
                                                         "tamano": 200}).json()
    claves = {c["algoritmo"]: c for c in r["resultado"]["comparativa"]}
    assert claves["reachability"]["resultado"]["coincide_con_bfs"] is True
    assert any("Subset-Sum" in a or "Suma de Subconjuntos" in a for a in r["resultado"]["avisos"])


def test_benchmark_validaciones_y_series():
    assert client.post("/api/complejidad/benchmark", json={"algoritmos": ["merge_sort"]}).status_code == 400
    assert client.post("/api/complejidad/benchmark", json={"algoritmos": ["merge_sort", "xxx"]}).status_code == 400
    r = client.post("/api/complejidad/benchmark", json={"algoritmos": ["insertion_sort", "merge_sort"], "tamano": 100,
                                                         "incluir_series": True, "tamanos_serie": [50, 100, 200]}).json()
    assert len(r["visualizacion"]["series"]) == 2


def test_catalogo():
    assert {c["clase"] for c in client.get("/api/complejidad/catalogo").json()} == {"P", "NP", "NSPACE"}


def test_explicar_cae_a_plantilla_sin_ollama():
    contrato = client.post("/api/lenguajes/automata", json=AFD).json()
    r = client.post("/api/explicar", json=contrato).json()
    assert r["fuente"] == "plantilla" and "ACEPTADA" in r["explicacion"]
    s = client.post("/api/explicar/stream", json=contrato)
    assert "plantilla" in s.text and "reemplazar" in s.text


def test_explicar_estado_sin_ollama():
    assert client.get("/api/explicar/estado").json()["activo"] is False
