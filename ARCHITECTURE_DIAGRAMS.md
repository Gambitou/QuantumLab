# QuantumLab - Architectural Diagrams (Mermaid)

Visualizaciones gráficas de la arquitectura del sistema.

---

## 1. Diagrama General de Capas

```mermaid
graph TB
    subgraph UI["🎨 PRESENTATION LAYER (Streamlit)"]
        Dashboard["Dashboard"]
        Hypotheses["Hypotheses CRUD"]
        Formulas["Formulas LaTeX"]
        Analyzer["Hypothesis Analyzer"]
        Relations["Relations Graph"]
        Reality["Reality Engine"]
    end
    
    subgraph LOGIC["🧠 LOGIC LAYER"]
        Repo["repositories.py<br/>(CRUD + Metrics)"]
        HypAna["hypothesis_analyzer.py<br/>(Semantic Analysis)"]
        RelGraph["relation_graph.py<br/>(Graph Viz)"]
        RealEngine["reality_engine.py<br/>(Simulations)"]
    end
    
    subgraph DATA["💾 DATA LAYER"]
        DB["database.py<br/>(Connection Manager)"]
        SQLite["SQLite<br/>quantumlab.db"]
    end
    
    subgraph AI["🧠 AI SUBSYSTEM"]
        AIConfig["ai/config.py"]
        LocalProv["LocalEmbeddingProvider<br/>(ST or Blake2b)"]
        GeminiProv["GeminiProvider<br/>(STUB)"]
    end
    
    Dashboard --> Repo
    Hypotheses --> Repo
    Formulas --> Repo
    Analyzer --> Repo
    Analyzer --> HypAna
    Relations --> Repo
    Relations --> RelGraph
    Reality --> RealEngine
    Reality --> Repo
    
    Repo --> DB
    HypAna --> LocalProv
    HypAna --> RelGraph
    
    DB --> SQLite
    LocalProv --> AIConfig
    GeminiProv --> AIConfig
    
    style UI fill:#e1f5ff
    style LOGIC fill:#f3e5f5
    style DATA fill:#e8f5e9
    style AI fill:#fff3e0
```

---

## 2. Dependency Graph (Módulos Core)

```mermaid
graph LR
    App["app.py"]
    
    App -->|init| DB["database.py"]
    App -->|render| Layout["ui/layout.py"]
    
    Layout -->|import| Pages["ui/pages/*"]
    
    Pages -->|uses| Repo["repositories.py"]
    Pages -->|uses| HypAna["hypothesis_analyzer.py"]
    Pages -->|uses| RelGraph["relation_graph.py"]
    Pages -->|uses| RealEngine["reality_engine.py"]
    Pages -->|uses| Styles["ui/styles.py"]
    
    Repo -->|query| DB
    HypAna -->|get data| Repo
    HypAna -->|embed| AI["ai/providers"]
    HypAna -->|graph| RelGraph
    RelGraph -->|uses| NX["NetworkX"]
    RelGraph -->|visualize| PyVis["PyVis"]
    RealEngine -->|compute| NumPy["NumPy"]
    RealEngine -->|integrate| SciPy["SciPy"]
    RealEngine -->|plot| Plotly["Plotly"]
    
    AI -->|fallback| LocalEmbed["LocalEmbeddingProvider"]
    LocalEmbed -->|try| ST["sentence-transformers"]
    LocalEmbed -->|fallback| Blake2b["Blake2b hash"]
    
    style App fill:#ffebee
    style DB fill:#e8f5e9
    style Repo fill:#f3e5f5
    style HypAna fill:#fce4ec
    style Pages fill:#e0f2f1
    style AI fill:#fff3e0
```

---

## 3. Data Flow: Create Hypothesis

```mermaid
sequenceDiagram
    participant UI as Streamlit Form
    participant Valid as Validation
    participant Repo as repositories.py
    participant DB as database.py
    participant SQLite as SQLite
    participant Render as Streamlit Render
    
    UI->>Valid: title, summary, status, tags
    alt title.strip() == ""
        Valid-->>UI: Error
    else Valid
        Valid->>Repo: create_hypothesis(...)
        Repo->>DB: get_connection()
        DB->>SQLite: INSERT
        SQLite-->>DB: lastrowid
        DB->>SQLite: COMMIT
        DB-->>Repo: connection closed
        Repo-->>Valid: id returned
        Valid-->>UI: Success
        UI->>Render: st.rerun()
    end
```

---

## 4. Data Flow: Hypothesis Analyzer

```mermaid
graph TD
    Start["User moves slider<br/>threshold = 0.26"]
    
    Start --> FetchData["Fetch Data<br/>list_hypotheses()<br/>list_relations()<br/>list_formulas()"]
    
    FetchData --> Analyze["analyze_hypotheses()"]
    
    Analyze --> Embeddings["Get Embeddings<br/>(ST or Blake2b)"]
    Analyze --> Similarity["Compute Similarity<br/>dot product"]
    Analyze --> Clustering["Clustering<br/>connected components"]
    Analyze --> Concepts["Concept Links<br/>token overlap"]
    Analyze --> Math["Math Matches<br/>LaTeX + keywords"]
    Analyze --> Contradictions["Contradiction Detection<br/>pattern matching"]
    Analyze --> Resonance["Idea Resonance<br/>composite score"]
    Analyze --> Insights["Generate Insights<br/>18 max"]
    
    Embeddings --> Result["AnalyzerResult<br/>(frozen namedtuple)"]
    Similarity --> Result
    Clustering --> Result
    Concepts --> Result
    Math --> Result
    Contradictions --> Result
    Resonance --> Result
    Insights --> Result
    
    Result --> Tabs["Display Tabs<br/>Heatmap | Resonance<br/>Clusters | Conflicts<br/>Math | Insights"]
    
    Tabs --> Display["Show Results<br/>(memory, no persistence)"]
    
    Display --> Optional["[Optional]<br/>User creates relation<br/>from suggestion"]
    
    Optional --> CreateRel["create_relation()<br/>→ BD"]
    
    style Start fill:#e3f2fd
    style FetchData fill:#f3e5f5
    style Analyze fill:#fce4ec
    style Result fill:#f1f8e9
    style Tabs fill:#e0f2f1
    style Display fill:#fbe9e7
    style Optional fill:#fff9c4
```

---

## 5. Database Schema Relationships

```mermaid
erDiagram
    hypotheses ||--o{ formulas : has
    hypotheses ||--o{ hypothesis_relations : source
    hypotheses ||--o{ hypothesis_relations : target
    hypotheses ||--o{ reality_simulations : associated
    
    hypotheses {
        int id PK
        string title
        text summary
        string status
        text tags
        datetime created_at
        datetime updated_at
    }
    
    formulas {
        int id PK
        int hypothesis_id FK
        string title
        text latex
        text notes
        datetime created_at
        datetime updated_at
    }
    
    hypothesis_relations {
        int id PK
        int source_hypothesis_id FK
        int target_hypothesis_id FK
        string label
        text notes
        float weight
        datetime created_at
        datetime updated_at
    }
    
    reality_simulations {
        int id PK
        string title
        string simulation_type
        text parameters
        text summary
        datetime created_at
    }
```

---

## 6. Module Dependency Matrix

```mermaid
graph LR
    subgraph Required["Required Dependencies"]
        ST["Streamlit"]
        SQLite["SQLite"]
        NX["NetworkX"]
        NP["NumPy"]
    end
    
    subgraph Optional["Optional Dependencies"]
        ST_Tr["sentence-transformers"]
        PyVis["PyVis"]
        SciPy["SciPy"]
        Plotly["Plotly"]
    end
    
    subgraph Internal["Internal Modules"]
        DB["database.py"]
        Repo["repositories.py"]
        HypAna["hypothesis_analyzer.py"]
        RelGraph["relation_graph.py"]
        RealEngine["reality_engine.py"]
    end
    
    DB --> SQLite
    Repo --> DB
    HypAna --> NP
    HypAna --> NX
    RelGraph --> NX
    RelGraph --> PyVis
    RealEngine --> NP
    RealEngine --> SciPy
    RealEngine --> Plotly
    HypAna --> ST_Tr
    
    style Required fill:#c8e6c9
    style Optional fill:#fff9c4
    style Internal fill:#bbdefb
```

---

## 7. Risk Heatmap (Severity vs Probability)

```mermaid
graph TB
    Critical["🔴 CRITICAL"]
    High["🟠 HIGH"]
    Medium["🟡 MEDIUM"]
    Low["🟢 LOW"]
    
    subgraph Critical
        C1["No validation<br/>of input"]
        C2["No DB indices"]
        C3["Zero tests"]
        C4["No logging"]
    end
    
    subgraph High
        H1["Dual similitude<br/>systems"]
        H2["Magic numbers"]
        H3["Mixed concerns<br/>in repositories"]
    end
    
    subgraph Medium
        M1["GeminiProvider<br/>unused"]
        M2["Analysis not<br/>persistent"]
        M3["Simulations no<br/>metadata"]
    end
    
    subgraph Low
        L1["LaTeX preview<br/>delayed"]
        L2["Offline mode<br/>unclear UX"]
    end
    
    style Critical fill:#ffcdd2
    style High fill:#ffe0b2
    style Medium fill:#fff9c4
    style Low fill:#c8e6c9
```

---

## 8. UI Navigation Graph

```mermaid
graph TB
    Sidebar["Sidebar<br/>st.radio"]
    
    Sidebar -->|"Panel"| Dashboard["render_dashboard()"]
    Sidebar -->|"Hipotesis"| Hypotheses["render_hypotheses()"]
    Sidebar -->|"Formulas"| Formulas["render_formulas()"]
    Sidebar -->|"Hypothesis Analyzer"| Analyzer["render_hypothesis_analyzer()"]
    Sidebar -->|"Relaciones"| Relations["render_relations()"]
    Sidebar -->|"Reality Engine"| Reality["render_reality_engine()"]
    
    Dashboard --> Metrics["5 Metrics"]
    Dashboard --> Recent["Recent Hypotheses<br/>& Formulas"]
    
    Hypotheses --> Create["Create Form"]
    Hypotheses --> List["List with Expanders"]
    Create --> CRUD1["CRUD Operations"]
    
    Formulas --> Create2["Create Form"]
    Formulas --> List2["Library"]
    Create2 --> CRUD2["CRUD Operations"]
    
    Analyzer --> Tabs1["5 Tabs"]
    Tabs1 --> Tab1["Visual Overview"]
    Tabs1 --> Tab2["Insights"]
    Tabs1 --> Tab3["Consistency"]
    Tabs1 --> Tab4["Math"]
    Tabs1 --> Tab5["Clusters"]
    
    Relations --> Manual["Manual Connection"]
    Relations --> Suggestions["Auto Suggestions"]
    Relations --> Graph["Interactive Graph"]
    Relations --> Clusters["Cluster Summary"]
    
    Reality --> Particles["Particles"]
    Reality --> Info["Information Field"]
    Reality --> Dynamics["Dynamics"]
    Reality --> Sandbox["Sandbox"]
    Reality --> Saved["Saved Simulations"]
    
    style Sidebar fill:#e1f5ff
    style Dashboard fill:#f1f8e9
    style Hypotheses fill:#f3e5f5
    style Analyzer fill:#fce4ec
    style Reality fill:#fff3e0
```

---

## 9. Analysis Pipeline Detail

```mermaid
graph TD
    Input["Hypotheses<br/>Relations<br/>Formulas"]
    
    Input --> Embed["🔹 Embedding<br/>(ST or Blake2b)"]
    Input --> Sim["🔹 Similarity<br/>(dot product)"]
    Input --> Concept["🔹 Concept Links<br/>(token overlap)"]
    Input --> Math["🔹 Math Matches<br/>(LaTeX + keywords)"]
    Input --> Contra["🔹 Contradictions<br/>(pattern matching)"]
    
    Embed --> Cluster["🟢 Clustering<br/>(connected comp)"]
    Sim --> Resonance["🟢 Idea Resonance<br/>(composite score)"]
    Concept --> Insights["🟢 Insights<br/>(logic rules)"]
    Math --> Insights
    Contra --> Insights
    Resonance --> Insights
    
    Cluster --> Result["AnalyzerResult"]
    Resonance --> Result
    Insights --> Result
    
    Result --> Viz["Visualization"]
    
    Viz --> Heatmap["Heatmap"]
    Viz --> ResonanceChart["Resonance Bar"]
    Viz --> ClusterScatter["Cluster Scatter"]
    Viz --> Connections["Connection Cards"]
    Viz --> ConflictCards["Conflict Cards"]
    Viz --> MathCards["Math Cards"]
    Viz --> InsightCards["Insight Cards"]
    
    style Input fill:#e3f2fd
    style Embed fill:#bbdefb
    style Sim fill:#bbdefb
    style Concept fill:#bbdefb
    style Math fill:#bbdefb
    style Contra fill:#bbdefb
    style Cluster fill:#c8e6c9
    style Resonance fill:#c8e6c9
    style Insights fill:#c8e6c9
    style Result fill:#a5d6a7
    style Viz fill:#fff9c4
```

---

## 10. Reality Engine Simulation Types

```mermaid
graph TB
    Start["Reality Engine<br/>User Input"]
    
    Start --> Choice["Select Simulation"]
    
    Choice -->|"Partículas"| Particles["simulate_particles()"]
    Choice -->|"Propagación"| Info["simulate_information_field()"]
    Choice -->|"Dinámicos"| Dynamics["simulate_dynamic_system()"]
    Choice -->|"Sandbox"| Sandbox["simulate_sandbox()"]
    
    Particles --> P1["particle_count<br/>steps, dt<br/>force_mode<br/>damping..."]
    P1 --> PSim["Loop: 140 steps<br/>calc accel<br/>update vel<br/>update pos<br/>quantize"]
    PSim --> PResult["frames[140,56,2]<br/>metrics dict"]
    
    Info --> I1["grid_size<br/>transmission_radius<br/>diffusion, decay..."]
    I1 --> ISim["Convolve2d<br/>diffusion update<br/>decay..."]
    ISim --> IResult["frames[110,56,56]<br/>time series"]
    
    Dynamics --> D1["system: Lorenz|Logistic<br/>steps, duration<br/>sigma, rho, beta..."]
    D1 --> DSim["scipy.solve_ivp()"]
    DSim --> DResult["trajectory 3D"]
    
    Sandbox --> S1["grid_size, density<br/>B3/S23 rule<br/>or expression"]
    S1 --> SSim["CA rules"]
    SSim --> SResult["frames[130,64,64]<br/>live_cells"]
    
    PResult --> Viz["Plotly Visualization"]
    IResult --> Viz
    DResult --> Viz
    SResult --> Viz
    
    Viz --> Save["[Optional]<br/>save_reality_simulation()"]
    
    style Particles fill:#c8e6c9
    style Info fill:#bbdefb
    style Dynamics fill:#ffe0b2
    style Sandbox fill:#f8bbd0
```

---

## 11. Error Handling & Validation Layers

```mermaid
graph TD
    UIInput["User Input<br/>Streamlit Form"]
    
    UIInput --> L1["🟡 Layer 1<br/>UI Validation<br/>(type checking)"]
    
    L1 --> L2["🟡 Layer 2<br/>Business Logic<br/>(repositories.py)<br/>.strip()"]
    
    L2 --> L3["🟢 Layer 3<br/>Database<br/>(sqlite3)<br/>FK, CHECK, UNIQUE"]
    
    L3 --> Result["✓ or ✗"]
    
    Result -->|Error| Catch1["Form Error<br/>st.error()"]
    Result -->|Error| Catch2["IntegrityError<br/>st.warning()"]
    Result -->|Error| Catch3["ValueError<br/>st.error()"]
    Result -->|Success| DB["Persist"]
    
    Note["⚠️ MISSING:<br/>- Max length validation<br/>- Regex validation<br/>- Pydantic schemas<br/>- Custom constraints"]
    
    style L1 fill:#fce4ec
    style L2 fill:#f3e5f5
    style L3 fill:#c8e6c9
    style Note fill:#ffcdd2
```

---

## 12. Improvement Roadmap (Phases)

```mermaid
timeline
    title QuantumLab Improvement Roadmap
    
    section Phase 1 (1-2w)
    Pytest suite : Add 70% coverage
    Pydantic validation : Input schemas
    Logging system : Centralized logs
    DB Indices : FK + status
    
    section Phase 2 (2-3w)
    Simulation timeout : AsyncIO integration
    Audit trail : Change tracking
    Unify similarity : One system
    Integration tests : Full flow
    
    section Phase 3 (3-4w)
    JSON export : Backup/share
    Full-text search : FTS5
    Analysis persistence : Save insights
    Versioning : Hypothesis snapshots
    
    section Phase 4 (4-5w)
    REST API : Programmatic access
    Gemini integration : Real cloud AI
    API docs : Swagger/OpenAPI
    CI/CD pipeline : GitHub Actions
```

---

**Diagramas generados con Mermaid**  
**Copiar bloques a tu herramienta favorita de visualización si necesario**

Referencia: https://mermaid.live/
