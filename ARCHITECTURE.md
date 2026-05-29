# QuantumLab Architecture Map

**Documento de Arquitectura del Sistema - 29 May 2026**

---

## 1️⃣ DIAGRAMA DE CAPAS

```
╔════════════════════════════════════════════════════════════════════════════╗
║                          CAPA DE PRESENTACIÓN (UI)                         ║
║                                 Streamlit                                   ║
├─────────────────┬──────────────────┬──────────────┬──────────┬──────────┬──┤
│   dashboard.py  │ hypotheses.py    │ formulas.py  │analyzer  │relations │RE║
│   - Metrics KPI │ - CRUD           │ - LaTeX      │- Semantic│- Grafo  │ui║
│   - Recent      │ - Status mgmt    │ - Preview    │- Cluster │- Network│pa║
│   - Charts      │ - Tags           │ - Ref        │- Insights│- Suggest│ge║
└─────────────────┴──────────────────┴──────────────┴──────────┴──────────┴──┘
                                      │
                ┌─────────────────────┼─────────────────────┐
                │                     │                     │
┌───────────────▼─────────────────────▼─────┐   ┌──────────▼────────────┐
│                                           │   │                       │
║          CAPA DE LÓGICA Y ANÁLISIS        ║   ║  CAPA DE UTILIDADES   ║
║                                           ║   ║                       ║
│ repositories.py                           │   │ ui/styles.py          │
│ ├─ CRUD (hypothesis, formula, relation)  │   │ ├─ Dark theme CSS     │
│ ├─ Dashboard metrics                      │   │ └─ Color palette      │
│ ├─ Suggest similar (cosine similarity)   │   │                       │
│ └─ Status options                         │   │ relation_graph.py     │
│                                           │   │ ├─ NetworkX builder   │
│ hypothesis_analyzer.py                   │   │ ├─ Pyvis HTML render  │
│ ├─ Semantic similarity (embeddings)      │   │ ├─ Clustering         │
│ ├─ Contradiction detection               │   │ └─ Colorization       │
│ ├─ Math concept extraction               │   │                       │
│ ├─ Clustering (connected components)    │   │ reality_engine.py     │
│ ├─ Idea Resonance scoring               │   │ ├─ Particle simulation│
│ └─ Automatic insights generation         │   │ ├─ Info field         │
│                                           │   │ ├─ Dynamics (Lorenz)  │
│ AI Provider Interface                     │   │ ├─ Sandbox (CA)       │
│ └─ get_embedding_provider()              │   │ └─ Safe AST eval      │
│                                           │   │                       │
└─────────────────────────────────────────────┘   └──────────────────────┘
        │                │                                │
        │ (1)            │ (2)                            │ (3)
        │ embeddings     │ list operations                │ DataFrame output
        │                │                                │
┌───────▼────────────────▼────────────────────────────────▼────────────────┐
║                      CAPA DE DATOS Y SERVICIOS                            ║
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  database.py                                                              │
│  ├─ SQLite connection context manager                                     │
│  ├─ Foreign key enforcement                                               │
│  └─ Auto-timestamp triggers                                               │
│                                                                            │
│  SQLite Database (quantumlab.db)                                          │
│  ├─ hypotheses                                                            │
│  ├─ formulas                                                              │
│  ├─ hypothesis_relations                                                  │
│  └─ reality_simulations                                                   │
│                                                                            │
│  ai/config.py + ai/providers/*                                            │
│  ├─ AIProviderConfig (env vars)                                           │
│  ├─ LocalEmbeddingProvider                                                │
│  │  ├─ sentence-transformers (si disponible)                             │
│  │  └─ Blake2b hashed fallback                                            │
│  └─ GeminiProvider (stub)                                                 │
│                                                                            │
│  External Libraries                                                       │
│  ├─ NumPy (matrices)                                                      │
│  ├─ SciPy (ODE, convolve)                                                │
│  ├─ NetworkX (grafo)                                                      │
│  ├─ Matplotlib (colormaps)                                                │
│  └─ Plotly (gráficos interactivos)                                        │
│                                                                            │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 2️⃣ MAPA DE MÓDULOS

```
quantumlab/
│
├──  __init__.py (APP_NAME)
├──  config.py (BASE_DIR, DATA_DIR, DATABASE_PATH)
│
├──  MÓDULOS CORE
│   ├── database.py
│   │   ├─ get_connection()              [Context Manager]
│   │   └─ initialize_database()         [Schema + Triggers]
│   │
│   ├── repositories.py                  [CRUD Layer]
│   │   ├─ Hypothesis: create/update/delete/list
│   │   ├─ Formula: create/delete/list
│   │   ├─ Relation: create/delete/list/relation_exists
│   │   ├─ Simulation: save/list/delete
│   │   ├─ Metrics: dashboard_metrics()
│   │   ├─ Suggestions: suggest_similar_hypotheses()  [Cosine sim]
│   │   └─ Helper: _rows_to_dicts(), _normalize_relation_ids()
│   │
│   ├── hypothesis_analyzer.py           [Analysis Engine]
│   │   ├─ analyze_hypotheses()          [Main entry]
│   │   ├─ _similarity_pairs()           [Embeddings → score]
│   │   ├─ _concept_links()              [Token overlap]
│   │   ├─ _clusters()                   [Connected components]
│   │   ├─ _contradictions()             [Pattern matching]
│   │   ├─ _math_matches()               [LaTeX + keywords]
│   │   ├─ _idea_resonance()             [Composite scoring]
│   │   └─ _insights()                   [Auto-generated findings]
│   │
│   ├── reality_engine.py                [Simulations]
│   │   ├─ simulate_particles()          [Particle dynamics]
│   │   ├─ simulate_information_field()  [Info propagation]
│   │   ├─ simulate_dynamic_system()     [Lorenz + Logistic]
│   │   ├─ simulate_sandbox()            [Cellular automata]
│   │   ├─ _safe_eval_expression()       [AST validation]
│   │   └─ Helper functions
│   │
│   └── relation_graph.py                [Graph Visualization]
│       ├─ build_networkx_graph()        [Graph builder]
│       ├─ cluster_map()                 [Connected components]
│       ├─ cluster_summary()             [Component details]
│       └─ render_pyvis_html()           [Interactive HTML]
│
├──  AI SUBSYSTEM
│   └── ai/
│       ├── __init__.py
│       ├── config.py                    [AIProviderConfig]
│       ├── providers/
│       │   ├── __init__.py
│       │   ├─ get_embedding_provider()
│       │   ├── base.py                  [EmbeddingProvider Protocol]
│       │   ├── local.py                 [LocalEmbeddingProvider]
│       │   │   ├─ sentence-transformers (dynamic import)
│       │   │   └─ Blake2b fallback
│       │   └── gemini.py                [GeminiProvider - STUB]
│
└──  UI SUBSYSTEM
    └── ui/
        ├── __init__.py
        ├── layout.py                    [Streamlit Router]
        │   └─ render_app()
        ├── styles.py                    [CSS Theme]
        │   └─ apply_dark_theme()
        │
        └── pages/                       [6 Pages]
            ├── __init__.py
            ├── dashboard.py             [KPI + Recent]
            ├── hypotheses.py            [CRUD]
            ├── formulas.py              [LaTeX]
            ├── analyzer.py              [Analysis UI]
            ├── relations.py             [Graph + Manual]
            └── reality.py               [4 Simulations]
```

---

## 3️⃣ FLUJO DE DATOS (End-to-End)

### **Caso 1: Usuario Crea Hipótesis**

```
┌─────────────────────────────────────────────────────────────────────┐
│ USER INPUT (UI - hypotheses.py)                                    │
│  title: "Coherencia cuántica en redes"                             │
│  summary: "..."                                                     │
│  status: "Borrador"                                                 │
│  tags: "cuántica, redes, simulación"                               │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│ VALIDATION (Streamlit form)                                        │
│  ✓ title.strip() != ""                                             │
│  ✗ No validación de longitud máxima                                │
│  ✗ No validación de caracteres especiales                          │
│  ✗ No validación de etiquetas duplicadas                           │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│ CRUD OPERATION (repositories.py)                                   │
│  create_hypothesis(title, summary, status, tags)                  │
│  └─ get_connection() context manager                              │
│     └─ INSERT INTO hypotheses (...)                                │
│        └─ lastrowid → id                                           │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│ DATABASE COMMIT                                                    │
│ quantumlab.db                                                       │
│ └─ hypotheses table:                                                │
│    id | title | summary | status | tags | created_at | updated_at │
│    11 | ...   | ...     | ...    | ...  | now        | now        │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│ UI REFRESH (st.rerun())                                            │
│  Streamlit re-ejecuta todo el script                               │
│  list_hypotheses() → fetch actualizado de BD                       │
│  Mostrar en expander                                                │
└─────────────────────────────────────────────────────────────────────┘
```

### **Caso 2: Usuario Ejecuta Hypothesis Analyzer**

```
┌──────────────────────────────────────────────────────────────────────┐
│ USER TRIGGER (analyzer.py - render_hypothesis_analyzer)            │
│  Movimiento slider: threshold = 0.26                                │
└────────────────────┬─────────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────────┐
│ DATA FETCH (repositories.py)                                        │
│  hypotheses = list_hypotheses()     → SELECT * ...                 │
│  relations = list_relations()       → SELECT * ...                 │
│  formulas = list_formulas()         → SELECT * ...                 │
│                                                                     │
│ Result: [3 listas de dicts con BD data]                             │
└────────────────────┬─────────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────────┐
│ ANALYSIS ENTRY (hypothesis_analyzer.py)                            │
│  result = analyze_hypotheses(hypotheses, relations, formulas, 0.26)│
└────────────────────┬─────────────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬─────────────────┐
        │            │            │                 │
        ▼            ▼            ▼                 ▼
   ┌────────┐  ┌──────────┐ ┌──────────┐  ┌──────────────┐
   │Embeddi │  │Similarity│ │Concept   │  │Contradiction │
   │ngs     │  │Pairs     │ │Links     │  │Detection     │
   │        │  │          │ │          │  │              │
   │vectors │  │→ Dot     │ │→ Token   │  │→ Pattern     │
   │= model │  │ Product  │ │ Overlap  │  │ Matching     │
   │.encode │  │ ≥0.26    │ │          │  │              │
   │        │  │          │ │          │  │              │
   │(1)     │  │(2)       │ │(3)       │  │(4)           │
   └────────┘  └──────────┘ └──────────┘  └──────────────┘
        │            │            │                 │
        │            ▼            │                 │
        │     ┌─────────────┐     │                 │
        │     │Clustering   │     │                 │
        │     │(Connected   │     │                 │
        │     │Components)  │     │                 │
        │     └─────────────┘     │                 │
        │            │            │                 │
        │            ▼            │                 │
        │    ┌─────────────┐      │                 │
        │    │Math Matches │      │                 │
        │    │LaTeX detect │      │                 │
        │    └─────────────┘      │                 │
        │            │            │                 │
        └────────────┼────────────┴─────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ Idea Resonance             │
        │ (composite scoring)        │
        │ = 46% semantic             │
        │  +28% graph degree         │
        │  +16% formula count        │
        │  +10% tag count            │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ Insights Generation        │
        │ (18 máx)                   │
        │                            │
        │ - Semantic connections     │
        │ - Contradictions           │
        │ - Incomplete hypotheses    │
        │ - Math suggestions         │
        │ - High resonance ideas     │
        └────────────┬───────────────┘
                     │
                     ▼
   ┌─────────────────────────────────────────┐
   │ AnalyzerResult (namedtuple frozen)     │
   ├─────────────────────────────────────────┤
   │ provider_mode: str                      │
   │ hypotheses: list[dict]                  │
   │ similarity_pairs: list[dict]            │
   │ clusters: list[dict]                    │
   │ contradictions: list[dict]              │
   │ math_matches: list[dict]                │
   │ insights: list[dict]                    │
   │ resonance: list[dict]                   │
   │ concept_links: list[dict]               │
   └────────────┬────────────────────────────┘
                │
                ▼
     (Solo en memoria - NO se guarda en BD)
           │
           ├─ Mostrando en tabs:
           │  ├─ Heatmap de similitud
           │  ├─ Gráfico Idea Resonance
           │  ├─ Clusters scatter
           │  ├─ Connections
           │  ├─ Contradictions
           │  ├─ Math suggestions
           │  └─ Insights
           │
           └─ Si usuario crea relación desde sugerencia:
              └─ create_relation() → BD
```

### **Caso 3: Usuario Ejecuta Simulación Reality Engine**

```
┌──────────────────────────────────────────────────────────────────┐
│ USER INPUT (reality.py - _render_particles)                     │
│                                                                  │
│ particle_count: 56                                               │
│ steps: 140                                                       │
│ dt: 0.05                                                         │
│ force_mode: "Oscilador central"                                  │
│ force_strength: 1.0                                              │
│ ... (más parámetros)                                             │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│ VALIDATION & EXECUTION                                          │
│                                                                  │
│ if force_mode == "Regla personalizada":                         │
│   ├─ Parse ax_expression (AST)                                   │
│   ├─ Whitelist check (solo funciones NumPy permitidas)          │
│   └─ Si falla → ValueError                                      │
│                                                                  │
│ result = simulate_particles(...)                                │
│  ├─ RNG initialization                                          │
│  ├─ Loop 140 steps:                                             │
│  │  ├─ Calcular aceleración                                     │
│  │  ├─ Actualizar velocidades                                   │
│  │  ├─ Limitar velocidad                                        │
│  │  ├─ Actualizar posiciones                                    │
│  │  ├─ Cuantizar si aplica                                      │
│  │  └─ Guardar frame                                            │
│  └─ Return SimulationResult                                     │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│ RESULT (NumPy arrays en memoria)                                │
│                                                                  │
│ SimulationResult:                                                │
│ ├─ frames: (140, 56, 2) ndarray  [steps, particles, xy]        │
│ ├─ metrics: {mean_speed, occupied_levels, ...}                 │
│ └─ series: {mean_speed, occupied_levels}  [time series]        │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│ VISUALIZATION (reality.py)                                      │
│                                                                  │
│ _particle_figure(result.frames, frame_index, animated=True)    │
│  └─ Plotly scatter plot                                         │
│                                                                  │
│ Metrics display:                                                │
│  ├─ Velocidad media: X.XXX                                      │
│  ├─ Niveles ocupados: N                                         │
│  └─ Límite: X.XX                                                │
│                                                                  │
│ Line chart (time series)                                        │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ├─ [Optional] Usuario hace click "Guardar"
                 │   └─ save_reality_simulation(...)
                 │      └─ INSERT INTO reality_simulations
                 │         ├─ title                                 
                 │         ├─ simulation_type: "Particulas"        
                 │         ├─ parameters: JSON (todos los params)  
                 │         └─ summary: metadata string             
                 │
                 └─ [Normal] Descarta al cambiar de tab
```

---

## 4️⃣ MAPA DE DEPENDENCIAS CRÍTICAS

### **Árbol de Dependencias (módulos Python)**

```
app.py
├─ database.initialize_database()
│  └─ get_connection() [context manager]
│     └─ SQLite connection
│
└─ ui/layout.render_app()
   ├─ ui/styles.apply_dark_theme()
   │  └─ Streamlit CSS injection
   │
   └─ PAGES dict
      ├─ render_dashboard
      │  └─ repositories.dashboard_metrics()
      │     └─ SELECT COUNT(*) from 4 tables
      │
      ├─ render_hypotheses
      │  ├─ repositories.list_hypotheses()
      │  ├─ repositories.create_hypothesis()
      │  ├─ repositories.update_hypothesis()
      │  └─ repositories.delete_hypothesis()
      │     └─ get_connection() → INSERT/UPDATE/DELETE
      │
      ├─ render_formulas
      │  ├─ repositories.list_hypotheses()
      │  ├─ repositories.list_formulas()
      │  ├─ repositories.create_formula()
      │  └─ repositories.delete_formula()
      │     └─ get_connection()
      │
      ├─ render_hypothesis_analyzer
      │  ├─ repositories.list_hypotheses()
      │  ├─ repositories.list_relations()
      │  ├─ repositories.list_formulas()
      │  └─ hypothesis_analyzer.analyze_hypotheses()
      │     ├─ ai/providers.get_embedding_provider()
      │     │  └─ LocalEmbeddingProvider()
      │     │     ├─ [TRY] sentence_transformers.SentenceTransformer
      │     │     └─ [FALLBACK] hashed embeddings (Blake2b)
      │     │
      │     ├─ NumPy operations
      │     ├─ NetworkX graph operations
      │     └─ Pattern matching (regex)
      │
      ├─ render_relations
      │  ├─ repositories.list_hypotheses()
      │  ├─ repositories.list_relations()
      │  ├─ repositories.suggest_similar_hypotheses()
      │  │  └─ cosine similarity (local, NO embeddings)
      │  │
      │  ├─ repositories.create_relation()
      │  ├─ repositories.delete_relation()
      │  └─ relation_graph.render_pyvis_html()
      │     ├─ NetworkX graph builder
      │     └─ PyVis network visualization
      │
      ├─ render_reality_engine
      │  ├─ reality_engine.simulate_particles/info/dynamics/sandbox()
      │  │  ├─ NumPy random
      │  │  ├─ SciPy integrate (ODE solver)
      │  │  ├─ SciPy convolve2d (information field)
      │  │  └─ AST validation for safe eval
      │  │
      │  ├─ reality_engine.plotly_colorscale()
      │  ├─ repositories.save_reality_simulation()
      │  ├─ repositories.list_reality_simulations()
      │  └─ repositories.delete_reality_simulation()
      │
      └─ [No UI direct calls to hypothesis_analyzer in analyzer.py]
         └─ analyzer.py calls it internally
```

### **Dependencias Externas Críticas**

```
requirements.txt:
├─ streamlit==1.45.1
│  └─ Used by: ALL pages (UI framework)
│
├─ networkx==3.5
│  └─ Used by:
│     ├─ hypothesis_analyzer._clusters()
│     ├─ hypothesis_analyzer._concept_links()
│     └─ relation_graph.render_pyvis_html()
│
├─ pyvis==0.3.2
│  └─ Used by: relation_graph.render_pyvis_html()
│
├─ numpy==2.4.6
│  └─ Used by:
│     ├─ hypothesis_analyzer (similarity matrix)
│     └─ reality_engine (all simulations)
│
├─ scipy==1.16.3
│  └─ Used by:
│     ├─ reality_engine.simulate_dynamic_system() [ODE]
│     └─ reality_engine.simulate_information_field() [convolve]
│
├─ matplotlib==3.10.7
│  └─ Used by: reality_engine.plotly_colorscale() [colormaps]
│
└─ plotly==6.5.0
   └─ Used by: ALL visualization pages

optional-requirements-ai.txt:
└─ sentence-transformers
   └─ Used by: ai/providers/local.py [dynamic import]
      Fallback: hashed embeddings (no dependency)
```

---

## 5️⃣ PUNTOS DÉBILES DEL DISEÑO

### **MATRIZ DE RIESGO**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SEVERIDAD vs PROBABILIDAD                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│    CRÍTICO ██████████ [CRITICAL ZONE]                                   │
│    ▲       ●                                                             │
│    │       (1) Falta de validación entrada                              │
│    │       (2) Sin índices BD                                            │
│    │       (3) Sin tests                                                │
│    │       (4) Sin logging                                              │
│    │                                                                     │
│   ALTO    ●●● [HIGH RISK]                                               │
│           (5) Deux sistemas similitud                                   │
│           (6) Magic numbers                                             │
│           (7) Mezcla concerns repositories                              │
│                                                                          │
│   MEDIO   ●● [MEDIUM]                                                   │
│           (8) GeminiProvider unused                                      │
│           (9) Análisis no persistente                                    │
│           (10) Simulaciones sin metadata                                 │
│                                                                          │
│   BAJO    ● [LOW]                                                       │
│           (11) Preview LaTeX diferido                                    │
│           (12) UX offline no clara                                       │
│                                                                          │
│   BAJA   MEDIA    ALTA     CRÍTICA                                      │
│   PROBABILIDAD →                                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

### **VULNERABILIDADES POR MÓDULO**

#### **🔴 repositories.py (HIGH RISK)**

```
┌──────────────────────────────────────────────────────┐
│ VULNERABILIDAD 1: Sin validación de entrada         │
├──────────────────────────────────────────────────────┤
│ Ubicación: create_hypothesis()                       │
│                                                      │
│ Código actual:                                       │
│   cursor = connection.execute(                       │
│     "INSERT INTO hypotheses (...) VALUES (?, ?, ..)"│
│     (title.strip(), summary.strip(), ...)           │
│   )                                                  │
│                                                      │
│ ⚠️ PROBLEMAS:                                        │
│  ✗ Sin límite de longitud                           │
│  ✗ Sin validación de caracteres                     │
│  ✗ Sin desduplicación de títulos                    │
│  ✗ Sin sanitización de etiquetas                    │
│  ✗ Sin check de BD consistency                      │
│                                                      │
│ RIESGO: Datos basura, duplicación, inconsistencia  │
└──────────────────────────────────────────────────────┘
```

#### **🔴 hypothesis_analyzer.py (EMBEDDING FALLIBILITY)**

```
┌──────────────────────────────────────────────────────┐
│ VULNERABILIDAD 2: Embeddings pueden fallar silente  │
├──────────────────────────────────────────────────────┤
│ Ubicación: LocalEmbeddingProvider.__init__()        │
│                                                      │
│ Código actual:                                       │
│   try:                                               │
│       self._model = SentenceTransformer(...)        │
│   except Exception:                                 │
│       self._model = None  # Fallback sin logueo    │
│                                                      │
│ ⚠️ PROBLEMAS:                                        │
│  ✗ Exception genérica (atrapa KeyboardInterrupt)   │
│  ✗ Sin logging de fallo                            │
│  ✗ Usuario no sabe si usa embeddings reales        │
│  ✗ Mode string es opaco                            │
│                                                      │
│ IMPACTO: Análisis con degradación silente           │
└──────────────────────────────────────────────────────┘
```

#### **🔴 reality_engine.py (TIMEOUT VULNERABLE)**

```
┌──────────────────────────────────────────────────────┐
│ VULNERABILIDAD 3: Sin timeout en simulaciones       │
├──────────────────────────────────────────────────────┤
│ Ubicación: simulate_particles() + otros             │
│                                                      │
│ Riesgo:                                             │
│  if steps=3000 → Streamlit timeout (30s default)   │
│  Usuario sin feedback                               │
│  No hay cancelación de largo proceso                │
│                                                      │
│ IMPACTO: Aplicación cuelga                          │
└──────────────────────────────────────────────────────┘
```

#### **🟡 relation_graph.py (NORMALIZATION COUPLING)**

```
┌──────────────────────────────────────────────────────┐
│ VULNERABILIDAD 4: Normalización de relaciones       │
├──────────────────────────────────────────────────────┤
│ Ubicación: repositories._normalize_relation_ids()  │
│            vs relation_graph (espera normalizado)   │
│                                                      │
│ ⚠️ PROBLEMAS:                                        │
│  ✗ Doble responsabilidad                           │
│  ✗ API confusa (¿quién normaliza?)                │
│  ✗ Si se olvida normalizar → resultados raros     │
│                                                      │
│ IMPACTO: Difícil de mantener                        │
└──────────────────────────────────────────────────────┘
```

#### **🟡 database.py (MISSING INDICES)**

```
┌──────────────────────────────────────────────────────┐
│ VULNERABILIDAD 5: Sin índices en ForeignKeys       │
├──────────────────────────────────────────────────────┤
│ Ubicación: initialize_database()                    │
│                                                      │
│ Consultas lentas:                                   │
│  SELECT * FROM hypothesis_relations                 │
│  WHERE source_hypothesis_id = ?;                    │
│  [FULL TABLE SCAN sin índice FK]                    │
│                                                      │
│ ⚠️ PROBLEMAS:                                        │
│  ✗ O(n) en vez de O(log n)                         │
│  ✗ Sin índice en tags (búsqueda lenta)            │
│  ✗ Sin índice en status (filtering lento)         │
│                                                      │
│ IMPACTO: Performance degrada con datos              │
└──────────────────────────────────────────────────────┘
```

---

## 6️⃣ FLUJO DE LLAMADAS A FUNCIONES (CALL GRAPH)

```
Streamlit Execution Loop (cada interacción usuario)
│
├─ [SETUP]
│  ├─ st.set_page_config()
│  └─ apply_dark_theme()
│
├─ [SIDEBAR]
│  └─ st.radio() → selecciona página
│
└─ [PAGE RENDER]
   │
   ├─ IF "Hipótesis"
   │  ├─ st.form("create_hypothesis")
   │  │  └─ create_hypothesis() + st.rerun()
   │  │     └─ get_connection() → INSERT
   │  │
   │  └─ list_hypotheses()
   │     └─ get_connection() → SELECT
   │        └─ st.expander + st.form("edit_hypothesis_N")
   │           ├─ update_hypothesis()
   │           │  └─ get_connection() → UPDATE
   │           │
   │           └─ delete_hypothesis()
   │              └─ get_connection() → DELETE
   │
   ├─ IF "Analyzer"
   │  ├─ list_hypotheses()
   │  ├─ list_relations()
   │  ├─ list_formulas()
   │  │  └─ get_connection() [3 queries]
   │  │
   │  ├─ analyze_hypotheses()
   │  │  ├─ get_embedding_provider()
   │  │  │  └─ LocalEmbeddingProvider()
   │  │  │     ├─ SentenceTransformer.encode() [FAST]
   │  │  │     │  OR
   │  │  │     └─ _hashed_embeddings() [FALLBACK]
   │  │  │
   │  │  ├─ _similarity_pairs()
   │  │  │  └─ np.dot(vectors, vectors.T)
   │  │  │
   │  │  ├─ _clusters()
   │  │  │  ├─ nx.Graph()
   │  │  │  └─ nx.connected_components()
   │  │  │
   │  │  ├─ _contradictions()
   │  │  │  └─ Pattern matching
   │  │  │
   │  │  ├─ _math_matches()
   │  │  │  └─ Regex LaTeX
   │  │  │
   │  │  └─ _insights()
   │  │     └─ Logic rules
   │  │
   │  ├─ st.tabs([...])
   │  │  ├─ TAB 1: _similarity_heatmap() → Plotly
   │  │  ├─ TAB 2: _render_insights() → Cards
   │  │  └─ TAB 3: _render_conflicts() → Warning UI
   │  │
   │  └─ [Optional] Si click "Guardar sugerencia"
   │     └─ create_relation()
   │        └─ get_connection() → INSERT
   │
   ├─ IF "Relaciones"
   │  ├─ list_hypotheses()
   │  ├─ list_relations()
   │  │
   │  ├─ _render_manual_connection()
   │  │  └─ create_relation() on submit
   │  │
   │  ├─ _render_suggestions()
   │  │  └─ suggest_similar_hypotheses()
   │  │     └─ Cosine similarity (local, NO embeddings)
   │  │
   │  ├─ _render_graph()
   │  │  ├─ build_networkx_graph()
   │  │  └─ render_pyvis_html()
   │  │     └─ Network visualization
   │  │
   │  └─ _render_clusters()
   │     └─ cluster_summary()
   │
   └─ IF "Reality Engine"
      ├─ _render_particles()
      │  ├─ simulate_particles()
      │  │  ├─ np.random.default_rng()
      │  │  ├─ [140 steps loop]
      │  │  │  └─ _safe_eval_expression() if custom
      │  │  │     └─ AST validation
      │  │  │
      │  │  └─ SimulationResult
      │  │
      │  ├─ _particle_figure() → Plotly
      │  │
      │  └─ [Optional] _save_panel()
      │     └─ save_reality_simulation()
      │        └─ get_connection() → INSERT JSON
      │
      └─ [Similar para otros 3 tipos de simulación]
```

---

## 7️⃣ MATRIZ DE INTERACCIÓN ENTRE MÓDULOS

```
              │ db │ repo │ analyzer │ graphs │ reality │ ai │ ui
──────────────┼────┼──────┼──────────┼────────┼─────────┼────┼────
database.py   │ ● │  ●   │    ●     │   ●    │    ●    │ ●  │ -
repositories  │ ● │  ●   │    ●     │   ●    │    ●    │ -  │ ●
hypothesis_a  │ - │  ●   │    ●     │   ●    │    -    │ ●  │ ●
relation_grap │ - │  ●   │    ●     │   ●    │    -    │ -  │ ●
reality_engi  │ - │  ●   │    -     │   -    │    ●    │ -  │ ●
ai/providers  │ - │  -   │    ●     │   -    │    -    │ ●  │ -
ui/pages/*    │ - │  ●   │    ●     │   ●    │    ●    │ -  │ ●

Legend:
● = Interacción directa (import/call)
- = No hay dependencia
```

**Lectura:**
- `database.py` interactúa con todos (es el hub)
- `repositories.py` es el segundo hub (CRUD para todos)
- `ui/pages/*` consume todo
- `ai/providers` es aislado (solo hypothesis_analyzer lo usa)
- `reality_engine.py` es relativamente independiente

---

## 8️⃣ PATRONES DE DATAFLOW

### **Patrón 1: BD → Memory → Visualization (lectura)**

```
SELECT from DB → Python dict list → Data processing → Streamlit widget
(synchronous, sin cache)
```

**Impacto:**
- ✅ Simple, predecible
- ❌ Sin optimización (refetch cada interacción)
- ❌ Sin incrementalidad (siempre full fetch)

### **Patrón 2: Memory → AST Validation → Execution (seguridad)**

```
User expression → AST parse → Whitelist check → Safe eval
(prevents code injection)
```

**Impacto:**
- ✅ Seguro para expresiones matemáticas
- ❌ Sin timeout (puede hanger en loop infinito)

### **Patrón 3: Embeddings → Matrix Math → Analysis (ML)**

```
Text → SentenceTransformer.encode() → np.ndarray → np.dot() → insights
    OR
Text → Blake2b hash → np.ndarray → np.dot() → insights (fallback)

(Graceful degradation)
```

**Impacto:**
- ✅ Robusto (siempre funciona)
- ❌ Silent fallback (usuario no sabe)

---

## 9️⃣ DIAGRAMA DE ESTADO (Hypothesis Lifecycle)

```
┌──────────────────────────────────────────────────┐
│          HYPOTHESIS STATE MACHINE                │
└──────────────────────────────────────────────────┘

                    ┌─────────────────────────────────────┐
                    │ ESTADO: Borrador                    │
                    │ (Inicial)                           │
                    └─────────────┬───────────────────────┘
                                  │
                    ┌─────────────▼───────────────────────┐
                    │ En estudio                          │
                    │ (Activa, en revisión)               │
                    └──────────────┬──────────────────────┘
                                   │
                ┌──────────────────┼──────────────────────┐
                │                  │                      │
         ┌──────▼─────┐    ┌──────▼──────┐    ┌──────────▼──────┐
         │ Validada    │    │ Descartada  │    │ (Volver a)      │
         │ (Aprobada)  │    │ (Rechazada) │    │ Borrador        │
         └─────────────┘    └─────────────┘    └─────────────────┘
         │        △           │       △              │
         │        └───────────┴───────┴──────────────┘
         │
         └─ Archivable (lógicamente)

OPERACIONES CRUD:
├─ create_hypothesis()    → state = Borrador
├─ update_hypothesis()    → state = cualquier
├─ delete_hypothesis()    → eliminado (CASCADE)
└─ list_hypotheses()      → filtrada por estado

NO IMPLEMENTADO:
├─ Transiciones automáticas
├─ Validaciones de estado
├─ Historial de transiciones
└─ Timestamps de cambio de estado
```

---

## 🔟 CAPAS DE VALIDACIÓN FALTANTES

```
┌────────────────────────────────────────────────────────────────┐
│                    VALIDATION LAYERS                           │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ LAYER 1: UI INPUT [STREAMLIT FORMS]                           │
│   ✓ Tipo de campo (text_input, textarea)                      │
│   ✗ Longitud máxima                                           │
│   ✗ Regex validation                                          │
│   ✗ Duplicate check                                           │
│                                                                │
│ LAYER 2: BUSINESS LOGIC [REPOSITORIES.PY]                     │
│   ✓ .strip() (limpia whitespace)                              │
│   ✗ Schema validation                                         │
│   ✗ Uniqueness constraints (excepto DB UNIQUE)               │
│   ✗ Relational integrity (excepto FK)                         │
│                                                                │
│ LAYER 3: DATABASE [SQLITE]                                    │
│   ✓ FOREIGN KEY enforcement                                   │
│   ✓ CHECK constraints                                         │
│   ✓ UNIQUE on (source, target, label)                         │
│   ✗ Índices (performance, no validation)                      │
│   ✗ Custom constraints (status transitions)                   │
│                                                                │
└────────────────────────────────────────────────────────────────┘

PROPUESTA: Agregar Pydantic schemas entre Streamlit ↔ repositories
```

---

## 1️⃣1️⃣ MAPA DE CONSISTENCIA DE DATOS

```
┌─────────────────────────────────────────────────────────────┐
│          CONSISTENCY INVARIANTS                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ✓ GARANTIZADO POR BD:                                      │
│   ├─ hypothesis.id es único (PK)                           │
│   ├─ formula.hypothesis_id → existe hypothesis            │
│   ├─ relation.source/target → existen hypotheses          │
│   ├─ relation.source ≠ relation.target                    │
│   └─ relation.(source, target, label) es único            │
│                                                             │
│ ⚠️ PARCIALMENTE GARANTIZADO:                               │
│   ├─ hypothesis.status ∈ {Borrador, En estudio, ...}     │
│   │   (ENUM no aplicado, solo sugerencia en app)          │
│   │                                                        │
│   └─ tags format (CSV, pero sin validación)               │
│                                                             │
│ ❌ NO GARANTIZADO:                                         │
│   ├─ No hay duplicadas de hypothesis por título           │
│   ├─ No hay control de duplicación de fórmulas            │
│   ├─ No hay auditoría de quién creó qué                   │
│   ├─ No hay transacciones distribuidas                    │
│   ├─ Si app se crashea: datos inconsistentes             │
│   └─ No hay backups automáticos                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 1️⃣2️⃣ RESUMEN EJECUTIVO: FORTALEZAS Y DEBILIDADES

### **FORTALEZAS ✅**

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│ 1. ARQUITECTURA MODULAR                                     │
│    Separación clara: UI ↔ Lógica ↔ Datos                  │
│    Fácil de testear componentes individuales               │
│                                                              │
│ 2. RESILENCIA DE IA                                        │
│    Embeddings confiables + fallback automático             │
│    No depende de conexión externa                          │
│                                                              │
│ 3. SEGURIDAD EN SIMULACIONES                               │
│    AST whitelist para expresiones personalizadas           │
│    No permite code injection                               │
│                                                              │
│ 4. ANÁLISIS INTELIGENTE                                    │
│    8 tipos de análisis automáticos                         │
│    Clustering, contradicciones, resonancia                │
│                                                              │
│ 5. VISUALIZACIÓN INTERACTIVA                               │
│    Pyvis network graph                                     │
│    Plotly charts con animación                             │
│                                                              │
│ 6. COMPLETAMENTE LOCAL                                     │
│    No envía datos a servidores externos                    │
│    Funciona offline                                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### **DEBILIDADES ❌**

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│ 1. SIN TESTING (CRÍTICO)                                   │
│    0% cobertura                                             │
│    Cambios rompen features silenciosamente                 │
│                                                              │
│ 2. VALIDACIÓN INSUFICIENTE                                 │
│    Entrada sin sanitización                                │
│    Datos basura posibles                                   │
│                                                              │
│ 3. SIN ÍNDICES BD                                          │
│    Queries degeneran con datos > 10k registros            │
│                                                              │
│ 4. DOS SISTEMAS DE SIMILITUD COMPETIDORES                 │
│    repositories.py (cosine local)                          │
│    hypothesis_analyzer.py (embeddings)                     │
│    Confusión sobre cuál usar                               │
│                                                              │
│ 5. ANÁLISIS NO PERSISTENTE                                 │
│    Insights se pierden al cerrar página                   │
│                                                              │
│ 6. SIN LOGGING                                             │
│    Difícil debuguear en producción                         │
│                                                              │
│ 7. SIN AUDITORÍA                                           │
│    No se sabe quién cambió qué y cuándo                   │
│                                                              │
│ 8. TIMEOUT VULNERABLE                                      │
│    Simulaciones largas cuelgan la app                      │
│                                                              │
│ 9. DOCUMENTACIÓN MÍNIMA                                    │
│    Difícil onboarding para nuevos devs                     │
│                                                              │
│ 10. GEMINI INTEGRATION INCOMPLETE                          │
│     Preparado pero no usable                               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 1️⃣3️⃣ ROADMAP DE MEJORAS (PRIORIZADO)

```
PHASE 1: ESTABILIZACIÓN (1-2 semanas)
├─ [P0] Agregar pytest + coverage mínima
├─ [P0] Validación con Pydantic en repositories
├─ [P0] Logging centralizado
└─ [P1] Índices en FK + status

PHASE 2: ROBUSTEZ (2-3 semanas)
├─ [P1] Timeout en simulaciones
├─ [P1] Auditoría de cambios
├─ [P1] Unificar sistemas de similitud
└─ [P1] Tests de integración

PHASE 3: FEATURES (3-4 semanas)
├─ [P2] Exportación JSON
├─ [P2] Búsqueda full-text (FTS5)
├─ [P2] Persistencia de análisis
└─ [P2] Versionamiento de simulaciones

PHASE 4: PRODUCTIZACIÓN (4-5 semanas)
├─ [P2] API REST
├─ [P2] Gemini integration real
├─ [P3] Documentación API
└─ [P3] CI/CD pipeline
```

---

**Documento generado**: 29 May 2026  
**Versión**: 1.0  
**Estado**: Analysis Complete ✅
