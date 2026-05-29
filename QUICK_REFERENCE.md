# QuantumLab - Quick Reference Map

**Mapa rápido de módulos, dependencias y flujos**

---

## MÓDULOS CORE

| Módulo | Responsabilidad | Líneas | Dependencias |
|--------|-----------------|--------|--------------|
| **database.py** | BD init, connection mgmt | ~130 | sqlite3 |
| **repositories.py** | CRUD + metrics + suggestions | ~380 | database.py |
| **hypothesis_analyzer.py** | Análisis semántico + clustering | ~430 | repositories, ai/providers, numpy, networkx |
| **relation_graph.py** | NetworkX graph + Pyvis HTML | ~180 | networkx, pyvis |
| **reality_engine.py** | 4 tipos de simulaciones | ~500+ | numpy, scipy, matplotlib, plotly |

---

## SUBSISTEMA AI

```
ai/providers/
├─ base.py          EmbeddingProvider (Protocol)
├─ local.py         LocalEmbeddingProvider
│                   ├─ SentenceTransformer (si instalado)
│                   └─ Blake2b fallback
├─ gemini.py        GeminiProvider (STUB)
└─ config.py        AIProviderConfig (env vars)
```

---

## UI PAGES

| Página | Función | Llamadas Clave |
|--------|---------|-----------------|
| **dashboard.py** | KPI + Recent | `dashboard_metrics()`, `list_hypotheses()`, `list_formulas()` |
| **hypotheses.py** | CRUD hipótesis | `create_hypothesis()`, `update_hypothesis()`, `delete_hypothesis()`, `list_hypotheses()` |
| **formulas.py** | CRUD fórmulas LaTeX | `create_formula()`, `list_formulas()`, `delete_formula()` |
| **analyzer.py** | Análisis inteligente | `analyze_hypotheses()`, `create_relation()` (from suggestions) |
| **relations.py** | Grafo interactivo | `build_networkx_graph()`, `render_pyvis_html()`, `create_relation()`, `suggest_similar_hypotheses()` |
| **reality.py** | 4 Simulaciones | `simulate_particles()`, `simulate_information_field()`, `simulate_dynamic_system()`, `simulate_sandbox()`, `save_reality_simulation()` |

---

## FLUJO PRINCIPAL

```
1. Usuario abre app
2. initialize_database()
3. render_app() → Streamlit layout
4. Usuario selecciona página
5. Página carga datos: list_hypotheses(), list_relations(), list_formulas()
6. Usuario interactúa (CRUD o análisis)
7. Operación: repositories.py → database.py → SQLite
8. st.rerun() → vuelve a paso 3
```

---

## DATAFLOW ANALYSIS

### **ENTRADA (Input)**
- Formularios Streamlit
- Sliders de simulaciones
- Expresiones matemáticas personalizadas

### **VALIDACIÓN**
- ✓ UI: tipo de campo
- ✓ Logic: .strip()
- ✓ DB: FK, CHECK, UNIQUE
- ✗ MISSING: Pydantic schemas, regex, longitud máxima

### **PROCESAMIENTO**
- CRUD → BD
- Análisis → En memoria (numpy, networkx)
- Simulaciones → Cálculo numérico

### **SALIDA**
- Métricas (st.metric)
- Tablas (st.dataframe, st.container)
- Gráficos (Plotly, Pyvis HTML)
- JSON (para guardar en BD)

---

## DEPENDENCIAS CRÍTICAS

### **DIRECTAS**
```
Streamlit          ← Todo el frontend
NetworkX          ← hypothesis_analyzer, relation_graph
NumPy             ← hypothesis_analyzer, reality_engine
SciPy             ← reality_engine (ODE, convolve)
Plotly            ← Todas las visualizaciones
PyVis             ← Grafo interactivo
Sentence-tr...    ← embeddings (OPTIONAL, tiene fallback)
```

### **INDIRECTAS**
```
sqlite3            ← database.py (built-in)
math, re, json     ← Varios módulos
collections        ← hypothesis_analyzer (Counter)
```

---

## RIESGOS CRÍTICOS (Risk Matrix)

### **P0: Crítico**
- [ ] Sin tests (0% coverage)
- [ ] Validación insuficiente
- [ ] Sin índices FK en BD

### **P1: Alto**
- [ ] Dos sistemas de similitud
- [ ] Magic numbers sin constantes
- [ ] Sin logging

### **P2: Medio**
- [ ] GeminiProvider no usado
- [ ] Análisis no persistente
- [ ] Sin auditoría

### **P3: Bajo**
- [ ] UX offline no clara
- [ ] Preview LaTeX diferido

---

## OPERACIONES POR MÓDULO

### **repositories.py**

```python
# Hypotheses
create_hypothesis(title, summary, status, tags) → id
update_hypothesis(id, title, summary, status, tags)
delete_hypothesis(id)
list_hypotheses() → [{...}, ...]

# Formulas
create_formula(title, latex, notes, hypothesis_id) → id
delete_formula(id)
list_formulas() → [{...}, ...]

# Relations
create_relation(source_id, target_id, label, notes, weight) → id
delete_relation(id)
list_relations() → [{...}, ...]
relation_exists(source_id, target_id) → bool
suggest_similar_hypotheses(threshold=0.18, limit=8) → [{...}, ...]

# Metrics
dashboard_metrics() → {hypotheses, formulas, relations, simulations, active}

# Simulations
save_reality_simulation(title, type, parameters, summary) → id
delete_reality_simulation(id)
list_reality_simulations() → [{...}, ...]
```

### **hypothesis_analyzer.py**

```python
analyze_hypotheses(
    hypotheses: list[dict],
    relations: list[dict],
    formulas: list[dict],
    similarity_threshold: float = 0.26
) → AnalyzerResult

# AnalyzerResult contiene:
# - provider_mode: str
# - hypotheses, similarity_pairs, clusters
# - contradictions, math_matches
# - insights, resonance, concept_links
```

### **reality_engine.py**

```python
simulate_particles(
    particle_count, steps, dt, force_mode, force_strength,
    damping, speed_limit, quantization_step, seed,
    ax_expression, ay_expression
) → SimulationResult

simulate_information_field(
    grid_size, steps, transmission_radius,
    diffusion, decay, pulse_strength
) → SimulationResult

simulate_dynamic_system(
    system_name, steps, duration,
    sigma, rho, beta, growth, initial_x
) → SimulationResult

simulate_sandbox(
    grid_size, steps, density, seed,
    rule_mode, rule_text
) → SimulationResult

# SimulationResult
frames: np.ndarray          # timesteps × data
metrics: dict[str, Any]
series: dict[str, np.ndarray]
```

### **relation_graph.py**

```python
build_networkx_graph(
    hypotheses: list[dict],
    relations: list[dict]
) → nx.Graph

render_pyvis_html(graph: nx.Graph) → str  # HTML string

cluster_map(graph: nx.Graph) → dict[int, int]      # node_id → cluster_id
cluster_summary(graph: nx.Graph) → list[list[int]] # clusters
```

---

## DATABASE SCHEMA (QUICK VIEW)

```sql
hypotheses
├─ id (PK, AI)
├─ title TEXT NOT NULL
├─ summary TEXT
├─ status TEXT (Borrador|En estudio|Validada|Descartada)
├─ tags TEXT
└─ timestamps (auto-update triggers)

formulas
├─ id (PK, AI)
├─ hypothesis_id (FK → hypotheses, ON DELETE SET NULL)
├─ title, latex, notes
└─ timestamps

hypothesis_relations
├─ id (PK, AI)
├─ source_hypothesis_id (FK → hypotheses, ON DELETE CASCADE)
├─ target_hypothesis_id (FK → hypotheses, ON DELETE CASCADE)
├─ label TEXT
├─ notes TEXT
├─ weight REAL
├─ UNIQUE(source, target, label)
├─ CHECK(source ≠ target)
└─ timestamps

reality_simulations
├─ id (PK, AI)
├─ title, simulation_type
├─ parameters TEXT (JSON)
├─ summary TEXT
└─ created_at
```

---

## PERFORMANCE NOTES

| Operación | Complejidad | Notas |
|-----------|-------------|-------|
| `list_hypotheses()` | O(n) | Full table scan, sin índices |
| `suggest_similar_hypotheses()` | O(n²) | Todos vs todos, cosine sim local |
| `analyze_hypotheses()` | O(n²) | Embeddings O(n·d), similarity O(n²) |
| `build_networkx_graph()` | O(n+m) | n=hipótesis, m=relaciones |
| `simulate_particles()` | O(steps·particles) | Loop directo, NumPy ops |
| `cluster_map()` | O(n+m) | Connected components |

⚠️ **SIN ÍNDICES**: Queries degeneran con > 10k hypotheses
⚠️ **SIN PAGINATION**: list_hypotheses() trae todo

---

## TESTING GAPS

| Aspecto | Status | Crítica |
|---------|--------|---------|
| Unit tests | ❌ NONE | SÍ |
| Integration tests | ❌ NONE | SÍ |
| UI tests | ❌ NONE | NO (Streamlit difícil) |
| Performance tests | ❌ NONE | SÍ |
| Security tests | ❌ NONE | MEDIA |
| Test coverage | 0% | CRÍTICA |

---

## DEPLOYMENT CHECKLIST

- [ ] Tests (mínimo 70% coverage)
- [ ] Logging configurado
- [ ] Índices en BD creados
- [ ] Validación con Pydantic
- [ ] Documentación API
- [ ] GitHub Actions CI/CD
- [ ] Docker container
- [ ] Backup strategy
- [ ] Monitoring/alerting
- [ ] Gemini integration (si necesario)

---

## COMANDOS ÚTILES (DEV)

```bash
# Ejecutar app
python -m streamlit run app.py

# Clean DB
rm data/quantumlab.db

# Reset venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Con AI local
pip install -r optional-requirements-ai.txt

# Future: Tests
pytest tests/ -v --cov=quantumlab

# Future: Type check
mypy quantumlab/
```

---

## ARCHIVO CENTRAL DE REFERENCIA

👉 **Consultar**: `ARCHITECTURE.md`
   - Diagramas ASCII detallados
   - Flujos end-to-end
   - Matriz de riesgos
   - Roadmap de mejoras

---

**Última actualización**: 29 May 2026
