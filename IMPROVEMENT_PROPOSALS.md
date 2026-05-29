# QuantumLab - Propuesta de Mejoras

**Soluciones propuestas para los problemas de diseño detectados**

---

## 🎯 ORGANIZACIÓN POR FASES

Las mejoras están priorizadas en 4 fases progresivas:
- **FASE 1 (1-2 semanas)**: Estabilización crítica
- **FASE 2 (2-3 semanas)**: Robustez y mantenibilidad
- **FASE 3 (3-4 semanas)**: Características y persistencia
- **FASE 4 (4-5 semanas)**: Productización y escala

---

## ⚡ FASE 1: ESTABILIZACIÓN CRÍTICA (P0)

### Problema 1: SIN TESTS (0% Coverage)

**Impacto:** CRÍTICO - Cambios rompen features silenciosamente

**Solución propuesta:**

```
📁 tests/
├── test_database.py
│   ├─ test_connection_context_manager()
│   ├─ test_initialize_database_schema()
│   ├─ test_foreign_keys_enforced()
│   └─ test_triggers_auto_update_timestamp()
│
├── test_repositories.py
│   ├─ test_create_hypothesis_valid_input()
│   ├─ test_create_hypothesis_empty_title_fails()
│   ├─ test_update_hypothesis_partial()
│   ├─ test_delete_hypothesis_cascades()
│   ├─ test_relation_normalization_idempotent()
│   ├─ test_suggest_similar_hypotheses_threshold()
│   └─ test_dashboard_metrics_consistency()
│
├── test_hypothesis_analyzer.py
│   ├─ test_analyze_hypotheses_empty_input()
│   ├─ test_similarity_pairs_sorted_by_score()
│   ├─ test_clustering_connected_components()
│   ├─ test_contradiction_detection_patterns()
│   ├─ test_math_matches_latex_detection()
│   ├─ test_idea_resonance_scoring_formula()
│   └─ test_embeddings_fallback_to_hashed()
│
├── test_reality_engine.py
│   ├─ test_simulate_particles_shape()
│   ├─ test_safe_eval_expression_whitelist()
│   ├─ test_safe_eval_expression_rejects_malicious()
│   ├─ test_simulate_information_field_decay()
│   └─ test_simulate_sandbox_cell_count()
│
├── test_relation_graph.py
│   ├─ test_build_networkx_graph_nodes()
│   ├─ test_cluster_map_connected_components()
│   └─ test_pyvis_html_generation()
│
└── conftest.py
   ├─ pytest fixtures (in-memory BD, sample data)
   └─ cleanup after each test
```

**Objetivo:** 70% coverage mínimo (80% ideal)

**Comando:**
```bash
pytest tests/ -v --cov=quantumlab --cov-report=html
```

---

### Problema 2: Validación Insuficiente

**Impacto:** CRÍTICO - Datos basura en BD, crashes

**Solución propuesta: Agregar Pydantic schemas**

```python
# quantumlab/schemas.py (NUEVO)

from pydantic import BaseModel, Field, validator

class HypothesisCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    summary: str = Field(default="", max_length=2000)
    status: str = Field(default="Borrador")
    tags: str = Field(default="", max_length=500)
    
    @validator("status")
    def status_valid(cls, v):
        if v not in ("Borrador", "En estudio", "Validada", "Descartada"):
            raise ValueError("Estado inválido")
        return v
    
    @validator("tags")
    def tags_valid(cls, v):
        if v.strip():
            tags = [t.strip() for t in v.split(",")]
            if any(len(t) > 50 for t in tags):
                raise ValueError("Etiqueta muy larga")
        return v

class HypothesisUpdate(HypothesisCreate):
    pass

class FormulaCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    latex: str = Field(..., min_length=5, max_length=1000)
    notes: str = Field(default="", max_length=1000)
    hypothesis_id: Optional[int] = None

class RelationCreate(BaseModel):
    source_hypothesis_id: int = Field(..., gt=0)
    target_hypothesis_id: int = Field(..., gt=0)
    label: str = Field(..., min_length=2, max_length=100)
    notes: str = Field(default="", max_length=500)
    weight: float = Field(default=1.0, ge=0.2, le=3.0)
    
    @validator("source_hypothesis_id", "target_hypothesis_id")
    def ids_different(cls, v, values):
        if "source_hypothesis_id" in values and v == values["source_hypothesis_id"]:
            raise ValueError("Source y target deben ser diferentes")
        return v
```

**Integración en repositories.py:**

```python
from quantumlab.schemas import HypothesisCreate

def create_hypothesis(title: str, summary: str, status: str, tags: str) -> int:
    # Validación
    schema = HypothesisCreate(title=title, summary=summary, status=status, tags=tags)
    
    # Proceed con schema.dict()
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO hypotheses (title, summary, status, tags) VALUES (?, ?, ?, ?)",
            (schema.title.strip(), schema.summary.strip(), schema.status, schema.tags.strip()),
        )
        return int(cursor.lastrowid)
```

---

### Problema 3: Sin Índices en BD

**Impacto:** CRÍTICO - Queries lentas con datos crecientes

**Solución propuesta: Agregar índices**

```python
# quantumlab/database.py - agregar después de CREATE TABLE

def initialize_database() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS hypotheses (
                -- esquema existente
            );
            
            -- ÍNDICES NUEVOS
            CREATE INDEX IF NOT EXISTS idx_hypotheses_status 
                ON hypotheses(status);
            
            CREATE INDEX IF NOT EXISTS idx_hypotheses_created_at 
                ON hypotheses(created_at DESC);
            
            -- Formulas
            CREATE TABLE IF NOT EXISTS formulas (
                -- esquema existente
            );
            
            CREATE INDEX IF NOT EXISTS idx_formulas_hypothesis_id 
                ON formulas(hypothesis_id);
            
            CREATE INDEX IF NOT EXISTS idx_formulas_created_at 
                ON formulas(created_at DESC);
            
            -- Relations
            CREATE TABLE IF NOT EXISTS hypothesis_relations (
                -- esquema existente
            );
            
            CREATE INDEX IF NOT EXISTS idx_relations_source 
                ON hypothesis_relations(source_hypothesis_id);
            
            CREATE INDEX IF NOT EXISTS idx_relations_target 
                ON hypothesis_relations(target_hypothesis_id);
            
            CREATE INDEX IF NOT EXISTS idx_relations_created_at 
                ON hypothesis_relations(created_at DESC);
            
            -- Simulations
            CREATE TABLE IF NOT EXISTS reality_simulations (
                -- esquema existente
            );
            
            CREATE INDEX IF NOT EXISTS idx_simulations_type 
                ON reality_simulations(simulation_type);
            
            CREATE INDEX IF NOT EXISTS idx_simulations_created_at 
                ON reality_simulations(created_at DESC);
            
            -- TRIGGERS (ya existen en versión actual)
            ...
            """
        )
```

**Impacto:** Queries pasan de O(n) a O(log n)

---

### Problema 4: Sin Logging Centralizado

**Impacto:** CRÍTICO - Imposible debuguear en producción

**Solución propuesta: Logging con structlog**

```python
# quantumlab/logging_config.py (NUEVO)

import logging
import structlog
from datetime import datetime

def configure_logging():
    """Setup centralized logging"""
    
    # Structlog configuration
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # File handler
    logging.basicConfig(
        format="%(message)s",
        stream=open("logs/quantumlab.log", "a"),
        level=logging.INFO,
    )

# Uso en código
logger = structlog.get_logger()

# En repositories.py
def create_hypothesis(title: str, summary: str, status: str, tags: str) -> int:
    logger.info("create_hypothesis", title=title, status=status)
    try:
        # operación
        logger.info("hypothesis_created", hypothesis_id=new_id, title=title)
        return new_id
    except Exception as e:
        logger.error("hypothesis_creation_failed", error=str(e), title=title, exc_info=True)
        raise
```

---

## 🔧 FASE 2: ROBUSTEZ Y MANTENIBILIDAD (P1)

### Problema 5: Dos Sistemas de Similitud Compitiendo

**Impacto:** ALTO - Confusión, mantenimiento difícil

**Solución propuesta: Unificar en hypothesis_analyzer.py**

```python
# quantumlab/repositories.py - REMOVER

def suggest_similar_hypotheses(...):
    # ELIMINAR ESTA FUNCIÓN
    # Usar hypothesis_analyzer en su lugar
    pass

# quantumlab/hypothesis_analyzer.py - MEJORAR

def suggest_related_hypotheses(
    hypotheses: list[dict],
    relations: list[dict],
    threshold: float = 0.26,
    exclude_existing: bool = True,
    limit: int = 8,
) -> list[dict]:
    """
    Sugerencias de relaciones basadas en similaridad semántica.
    
    Uses embeddings + conectividad existente.
    """
    provider = get_embedding_provider()
    vectors = provider.encode([_hypothesis_text(h) for h in hypotheses])
    similarity = vectors @ vectors.T
    
    # Índice de relaciones existentes
    existing = set()
    for rel in relations:
        sid, tid = min(rel["source_hypothesis_id"], rel["target_hypothesis_id"]), \
                   max(rel["source_hypothesis_id"], rel["target_hypothesis_id"])
        existing.add((sid, tid))
    
    # Generar sugerencias
    suggestions = []
    for i, j in itertools.combinations(range(len(hypotheses)), 2):
        if (hypotheses[i]["id"], hypotheses[j]["id"]) in existing:
            continue
        score = float(similarity[i, j])
        if score >= threshold:
            suggestions.append({
                "source_id": hypotheses[i]["id"],
                "source_title": hypotheses[i]["title"],
                "target_id": hypotheses[j]["id"],
                "target_title": hypotheses[j]["title"],
                "score": score,
                "method": "semantic_embeddings",  # Distinguir del anterior
            })
    
    return sorted(suggestions, key=lambda x: x["score"], reverse=True)[:limit]
```

**En UI (pages/relations.py):**
```python
from quantumlab.hypothesis_analyzer import suggest_related_hypotheses

def _render_suggestions() -> None:
    suggestions = suggest_related_hypotheses(
        list_hypotheses(),
        list_relations(),
        threshold=0.26
    )
    # ... mostrar sugerencias
```

---

### Problema 6: Magic Numbers Esparcidos

**Impacto:** ALTO - Código frágil, difícil de ajustar

**Solución propuesta: Centralizar en constants.py**

```python
# quantumlab/constants.py (NUEVO)

# Thresholds for similarity
SIMILARITY_THRESHOLD_DEFAULT = 0.26
SIMILARITY_THRESHOLD_HIGH = 0.72
SIMILARITY_THRESHOLD_MEDIUM = 0.46
SIMILARITY_THRESHOLD_LOW = 0.18

# Concept links strength threshold
CONCEPT_LINK_STRENGTH_THRESHOLD = 0.34

# Idea Resonance scoring weights
RESONANCE_WEIGHT_SEMANTIC = 0.46
RESONANCE_WEIGHT_GRAPH = 0.28
RESONANCE_WEIGHT_FORMULAS = 0.16
RESONANCE_WEIGHT_TAGS = 0.10

RESONANCE_SCORE_HIGH = 65
RESONANCE_SCORE_MEDIUM = 35

# Contradiction patterns priorities
CONTRADICTION_PRIORITY_HIGH = 0.25
CONTRADICTION_PRIORITY_MEDIUM = 0.10

# UI Colors
COLORS_PALETTE = (
    "#22d3ee",    # cyan
    "#a3e635",    # lime
    "#f59e0b",    # amber
    "#f472b6",    # pink
    "#818cf8",    # indigo
    "#34d399",    # emerald
    "#fb7185",    # rose
    "#c084fc",    # fuchsia
)

COLOR_ERROR = "#fb7185"
COLOR_WARNING = "#f59e0b"
COLOR_SUCCESS = "#22d3ee"

# Database
DATABASE_VACUUM_THRESHOLD = 50000  # rows
BATCH_SIZE_DEFAULT = 16  # embeddings

# Status options
HYPOTHESIS_STATUSES = ("Borrador", "En estudio", "Validada", "Descartada")
HYPOTHESIS_STATUS_DEFAULT = "Borrador"

# Limitations
MAX_HYPOTHESES_PER_PAGE = 100
MAX_RECENT_ITEMS = 5
MAX_INSIGHTS = 18
MAX_SUGGESTIONS = 8
MAX_TITLE_LENGTH = 200
MAX_SUMMARY_LENGTH = 2000
MIN_TITLE_LENGTH = 3

# Reality Engine
PARTICLE_COUNT_MIN = 8
PARTICLE_COUNT_MAX = 180
STEPS_MIN = 30
STEPS_MAX = 300
SPEED_LIMIT_MIN = 0.1
SPEED_LIMIT_MAX = 4.0
```

**Uso en código:**
```python
# hypothesis_analyzer.py
from quantumlab.constants import SIMILARITY_THRESHOLD_DEFAULT, RESONANCE_WEIGHT_SEMANTIC

def analyze_hypotheses(
    hypotheses: list[dict],
    relations: list[dict],
    formulas: list[dict],
    similarity_threshold: float = SIMILARITY_THRESHOLD_DEFAULT,  # Usar constante
) -> AnalyzerResult:
    # ...
    score = 100 * (
        RESONANCE_WEIGHT_SEMANTIC * semantic_score
        + RESONANCE_WEIGHT_GRAPH * graph_score
        + RESONANCE_WEIGHT_FORMULAS * formula_score
        + RESONANCE_WEIGHT_TAGS * tag_score
    )
```

---

### Problema 7: Mezcla de Concerns en repositories.py

**Impacto:** ALTO - Difícil de testear, mantener, extender

**Solución propuesta: Separar en múltiples módulos**

```
quantumlab/
├── repositories/
│   ├── __init__.py
│   ├── hypothesis_repo.py      (create, update, delete, list hypotheses)
│   ├── formula_repo.py         (CRUD formulas)
│   ├── relation_repo.py        (CRUD relations + helpers)
│   ├── simulation_repo.py      (CRUD simulations)
│   ├── metrics_repo.py         (dashboard metrics)
│   └── base.py                 (BaseRepository mixin)

# quantumlab/repositories/hypothesis_repo.py

from quantumlab.schemas import HypothesisCreate, HypothesisUpdate
from quantumlab.constants import HYPOTHESIS_STATUSES

class HypothesisRepository:
    @staticmethod
    def create(hypothesis: HypothesisCreate) -> int:
        """Create new hypothesis"""
        # ...
    
    @staticmethod
    def update(id: int, hypothesis: HypothesisUpdate) -> None:
        """Update hypothesis"""
        # ...
    
    @staticmethod
    def delete(id: int) -> None:
        """Delete hypothesis (cascade to relations)"""
        # ...
    
    @staticmethod
    def list(
        status: Optional[str] = None,
        limit: int = None,
        offset: int = 0
    ) -> list[dict]:
        """List hypotheses with optional filtering"""
        # ...
    
    @staticmethod
    def get_by_id(id: int) -> dict:
        """Get single hypothesis"""
        # ...
    
    @staticmethod
    def get_statistics() -> dict:
        """Stats: count by status, avg relations, etc"""
        # ...

# quantumlab/repositories/__init__.py - mantener compatibilidad

from quantumlab.repositories.hypothesis_repo import HypothesisRepository
from quantumlab.repositories.formula_repo import FormulaRepository
# ... etc

# Aliases para compatibilidad con código existente
create_hypothesis = HypothesisRepository.create
update_hypothesis = HypothesisRepository.update
delete_hypothesis = HypothesisRepository.delete
list_hypotheses = HypothesisRepository.list
# ... etc
```

**Beneficios:**
- Cada repo es testeable independientemente
- Código más limpio y modular
- Fácil agregar nuevas funcionalidades
- Mejor separación de responsabilidades

---

## 📈 FASE 3: CARACTERÍSTICAS Y PERSISTENCIA (P2)

### Problema 8: Análisis No Persistente

**Impacto:** MEDIO - Insights se pierden al cerrar página

**Solución propuesta: Tabla analysis_cache**

```python
# quantumlab/database.py - agregar tabla

def initialize_database() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS analysis_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hypothesis_ids TEXT NOT NULL,           -- JSON array
                analysis_type TEXT NOT NULL,             -- "full", "quick"
                threshold REAL NOT NULL,
                provider_mode TEXT NOT NULL,             -- "sentence-transformers", "hashed"
                similarity_pairs TEXT NOT NULL,          -- JSON
                clusters TEXT NOT NULL,                  -- JSON
                contradictions TEXT NOT NULL,            -- JSON
                insights TEXT NOT NULL,                  -- JSON
                resonance TEXT NOT NULL,                 -- JSON
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT NOT NULL,                -- 7 days default
                UNIQUE(hypothesis_ids, analysis_type, threshold)
            );
            
            CREATE INDEX IF NOT EXISTS idx_analysis_created_at 
                ON analysis_cache(created_at DESC);
            
            CREATE INDEX IF NOT EXISTS idx_analysis_expires 
                ON analysis_cache(expires_at);
            """
        )

# quantumlab/repositories/analysis_repo.py (NUEVO)

class AnalysisRepository:
    @staticmethod
    def cache_analysis(
        hypothesis_ids: list[int],
        analysis_type: str,
        threshold: float,
        result: AnalyzerResult
    ) -> None:
        """Cache analysis results"""
        with get_connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO analysis_cache
                (hypothesis_ids, analysis_type, threshold, provider_mode, 
                 similarity_pairs, clusters, contradictions, insights, resonance,
                 expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', '+7 days'))
                """,
                (
                    json.dumps(sorted(hypothesis_ids)),
                    analysis_type,
                    threshold,
                    result.provider_mode,
                    json.dumps(result.similarity_pairs),
                    json.dumps(result.clusters),
                    json.dumps(result.contradictions),
                    json.dumps(result.insights),
                    json.dumps(result.resonance),
                )
            )
    
    @staticmethod
    def get_cached_analysis(
        hypothesis_ids: list[int],
        analysis_type: str,
        threshold: float
    ) -> Optional[AnalyzerResult]:
        """Get cached analysis if exists"""
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT * FROM analysis_cache
                WHERE hypothesis_ids = ? 
                  AND analysis_type = ?
                  AND threshold = ?
                  AND expires_at > datetime('now')
                LIMIT 1
                """,
                (json.dumps(sorted(hypothesis_ids)), analysis_type, threshold)
            ).fetchone()
        
        if not row:
            return None
        
        return AnalyzerResult(
            provider_mode=row["provider_mode"],
            similarity_pairs=json.loads(row["similarity_pairs"]),
            # ... etc
        )
    
    @staticmethod
    def cleanup_expired():
        """Remove expired cache entries (run periodically)"""
        with get_connection() as connection:
            connection.execute(
                "DELETE FROM analysis_cache WHERE expires_at <= datetime('now')"
            )

# Uso en pages/analyzer.py

from quantumlab.repositories.analysis_repo import AnalysisRepository

def render_hypothesis_analyzer() -> None:
    hypotheses = list_hypotheses()
    threshold = st.slider(...)
    
    # Intentar cache
    cached = AnalysisRepository.get_cached_analysis(
        [h["id"] for h in hypotheses],
        "full",
        threshold
    )
    
    if cached:
        result = cached
        st.info("📦 Resultados en caché (7 días)")
    else:
        result = analyze_hypotheses(hypotheses, ...)
        AnalysisRepository.cache_analysis(
            [h["id"] for h in hypotheses],
            "full",
            threshold,
            result
        )
    
    # ... mostrar resultados
```

---

### Problema 9: Simulaciones sin Metadata

**Impacto:** MEDIO - Imposible reproducir o entender contexto

**Solución propuesta: Extender reality_simulations**

```python
# quantumlab/database.py - mejorar tabla

def initialize_database() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            ALTER TABLE reality_simulations ADD COLUMN (
                description TEXT,                        -- descripción larga
                tags TEXT,                               -- "chaos, particles"
                parent_simulation_id INTEGER,            -- para variaciones
                hypothesis_ids TEXT,                     -- JSON array de IDs
                expected_outcome TEXT,                   -- predicción
                actual_outcome TEXT,                     -- resultado
                successful BOOLEAN DEFAULT NULL,         -- ¿validó hipótesis?
                frames_count INTEGER,                    -- cuántos frames generados
                execution_time_ms REAL,                  -- tiempo de ejecución
                notes TEXT
            );
            """
        )

# Actualizar save_reality_simulation()

def save_reality_simulation(
    title: str,
    simulation_type: str,
    parameters: dict,
    summary: str,
    description: str = "",
    tags: str = "",
    hypothesis_ids: list[int] = None,
    expected_outcome: str = "",
) -> int:
    """Save simulation with extended metadata"""
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO reality_simulations (
                title, simulation_type, parameters, summary,
                description, tags, hypothesis_ids,
                expected_outcome, frames_count, execution_time_ms,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title.strip(),
                simulation_type.strip(),
                json.dumps(parameters),
                summary.strip(),
                description.strip(),
                tags.strip(),
                json.dumps(hypothesis_ids or []),
                expected_outcome.strip(),
                parameters.get("frames_count", 0),
                parameters.get("execution_time_ms", 0),
                datetime.now().isoformat(),
            ),
        )
        return int(cursor.lastrowid)
```

---

### Problema 10: Falta de Búsqueda Full-Text

**Impacto:** MEDIO - No hay forma de encontrar cosas

**Solución propuesta: FTS5 virtual table**

```python
# quantumlab/database.py

def initialize_database() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            -- Full-text search virtual table
            CREATE VIRTUAL TABLE IF NOT EXISTS hypotheses_fts USING fts5(
                id UNINDEXED,
                title,
                summary,
                tags,
                content=hypotheses,
                content_rowid=id
            );
            
            -- Trigger para mantener FTS sincronizado
            CREATE TRIGGER IF NOT EXISTS hypotheses_ai AFTER INSERT ON hypotheses BEGIN
              INSERT INTO hypotheses_fts(rowid, title, summary, tags) 
              VALUES (new.id, new.title, new.summary, new.tags);
            END;
            
            CREATE TRIGGER IF NOT EXISTS hypotheses_ad AFTER DELETE ON hypotheses BEGIN
              INSERT INTO hypotheses_fts(hypotheses_fts, rowid, title, summary, tags)
              VALUES('delete', old.id, old.title, old.summary, old.tags);
            END;
            
            CREATE TRIGGER IF NOT EXISTS hypotheses_au AFTER UPDATE ON hypotheses BEGIN
              INSERT INTO hypotheses_fts(hypotheses_fts, rowid, title, summary, tags)
              VALUES('delete', old.id, old.title, old.summary, old.tags);
              INSERT INTO hypotheses_fts(rowid, title, summary, tags)
              VALUES (new.id, new.title, new.summary, new.tags);
            END;
            """
        )

# quantumlab/repositories/search_repo.py (NUEVO)

class SearchRepository:
    @staticmethod
    def search_hypotheses(query: str, limit: int = 20) -> list[dict]:
        """Full-text search in hypotheses"""
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT h.* FROM hypotheses h
                WHERE h.id IN (
                    SELECT id FROM hypotheses_fts WHERE hypotheses_fts MATCH ?
                )
                ORDER BY rank
                LIMIT ?
                """,
                (query, limit)
            ).fetchall()
            return _rows_to_dicts(rows)
    
    @staticmethod
    def search_all(query: str, limit: int = 50) -> dict:
        """Search across all entities"""
        return {
            "hypotheses": SearchRepository.search_hypotheses(query, limit // 3),
            "formulas": SearchRepository.search_formulas(query, limit // 3),
            "relations": SearchRepository.search_relations(query, limit // 3),
        }

# Uso en UI - nueva página o modal

def render_search():
    query = st.text_input("Buscar...", placeholder="Escribe para buscar")
    if query:
        results = SearchRepository.search_all(query)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader(f"Hipótesis ({len(results['hypotheses'])})")
            for h in results['hypotheses']:
                st.write(h['title'])
        
        with col2:
            st.subheader(f"Fórmulas ({len(results['formulas'])})")
            for f in results['formulas']:
                st.write(f['title'])
        
        with col3:
            st.subheader(f"Relaciones ({len(results['relations'])})")
            for r in results['relations']:
                st.write(r['label'])
```

---

## 🚀 FASE 4: PRODUCTIZACIÓN (P3)

### Problema 11: Sin API REST

**Impacto:** BAJO-MEDIO - Integración externa imposible

**Solución propuesta: FastAPI wrapper**

```python
# quantumlab/api/app.py (NUEVO)

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from quantumlab.repositories import (
    HypothesisRepository,
    FormulaRepository,
    RelationRepository,
)

app = FastAPI(
    title="QuantumLab API",
    version="1.0.0",
    description="Research workspace API"
)

# Endpoints Hypotheses
@app.get("/api/v1/hypotheses")
def list_hypotheses(skip: int = 0, limit: int = 20):
    """List all hypotheses"""
    return HypothesisRepository.list(offset=skip, limit=limit)

@app.post("/api/v1/hypotheses")
def create_hypothesis(hypothesis: HypothesisCreate):
    """Create new hypothesis"""
    id = HypothesisRepository.create(hypothesis)
    return {"id": id, "message": "Created"}

@app.get("/api/v1/hypotheses/{id}")
def get_hypothesis(id: int):
    """Get hypothesis by ID"""
    hyp = HypothesisRepository.get_by_id(id)
    if not hyp:
        raise HTTPException(status_code=404)
    return hyp

@app.put("/api/v1/hypotheses/{id}")
def update_hypothesis(id: int, hypothesis: HypothesisUpdate):
    """Update hypothesis"""
    HypothesisRepository.update(id, hypothesis)
    return {"message": "Updated"}

@app.delete("/api/v1/hypotheses/{id}")
def delete_hypothesis(id: int):
    """Delete hypothesis"""
    HypothesisRepository.delete(id)
    return {"message": "Deleted"}

# Endpoints Analysis
@app.get("/api/v1/analyze/{hypothesis_id}")
def analyze_hypothesis(hypothesis_id: int, threshold: float = 0.26):
    """Run analysis on a hypothesis"""
    hypotheses = list_hypotheses()
    result = analyze_hypotheses(hypotheses, threshold=threshold)
    return result.dict()

# Ejecutar con: uvicorn quantumlab.api.app:app --reload
```

**Documentación automática:** FastAPI genera swagger en `/docs`

---

### Problema 12: Gemini Provider Completo

**Impacto:** BAJO - Integración cloud opcional

**Solución propuesta: Implementar GeminiProvider**

```python
# quantumlab/ai/providers/gemini.py - COMPLETAR

import google.generativeai as genai
from quantumlab.ai.config import AI_CONFIG

class GeminiProvider:
    def __init__(self):
        self.name = "Gemini Provider"
        self.mode = "gemini-api"
        if not AI_CONFIG.enable_external_calls:
            raise RuntimeError("Gemini API is disabled (set QUANTUMLAB_ENABLE_EXTERNAL_AI=1)")
        
        genai.configure(api_key=AI_CONFIG.gemini_api_key)
        self.model = genai.GenerativeModel("gemini-pro")
    
    def encode(self, texts: list[str]) -> np.ndarray:
        """Usar Gemini embeddings (si disponible en futuro)"""
        # Por ahora fallback a local
        from quantumlab.ai.providers.local import LocalEmbeddingProvider
        return LocalEmbeddingProvider().encode(texts)
    
    def analyze_hypothesis(self, hypothesis: dict) -> str:
        """Use Gemini to analyze hypothesis"""
        prompt = f"""
        Analiza esta hipótesis y proporciona insights:
        
        Título: {hypothesis['title']}
        Resumen: {hypothesis['summary']}
        Etiquetas: {hypothesis['tags']}
        
        Proporciona:
        1. Explicación clara
        2. Posibles test/experimentos
        3. Relación con otras disciplinas
        4. Limitaciones potenciales
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def suggest_contradictions(self, hypotheses: list[dict]) -> list[dict]:
        """Use Gemini to find contradictions"""
        prompt = f"""
        Analiza estas {len(hypotheses)} hipótesis y encuentra posibles contradicciones:
        
        {json.dumps([{'title': h['title'], 'summary': h['summary']} for h in hypotheses])}
        
        Formato: JSON array con {{source_title, target_title, contradiction, severity}}
        """
        
        response = self.model.generate_content(prompt)
        return json.loads(response.text)
```

---

## 📋 TABLA COMPARATIVA DE SOLUCIONES

| Problema | Solución | Complejidad | Impacto | Tiempo |
|----------|----------|------------|--------|---------|
| Sin tests | Pytest suite + fixtures | Media | Crítico | 1 sem |
| Validación pobre | Pydantic schemas | Media | Crítico | 3 días |
| Sin índices | Agregar índices SQL | Baja | Crítico | 1 día |
| Sin logging | structlog + file handler | Media | Crítico | 2 días |
| Dual similitud | Unificar en analyzer | Media | Alto | 2 días |
| Magic numbers | Constants.py | Baja | Alto | 1 día |
| Concerns mezclados | Refactor en submódulos | Alta | Alto | 1 sem |
| Análisis no persistent | analysis_cache table | Media | Medio | 3 días |
| Sin metadata simulaciones | Extender schema | Baja | Medio | 1 día |
| Sin búsqueda | FTS5 virtual table | Media | Medio | 2 días |
| Sin API | FastAPI wrapper | Media | Bajo | 3 días |
| Gemini incompleto | Implementar real | Media | Bajo | 2 días |

---

## 🎯 RECOMENDACIÓN DE PRIORIZACIÓN

### Inmediato (Este mes)
1. **Tests** - Sin esto, no se puede cambiar nada
2. **Validación Pydantic** - Evita datos corruptos
3. **Índices BD** - Performance
4. **Logging** - Debugging

### Corto plazo (Próximo mes)
5. Unificar similitud
6. Constants.py
7. Refactor repositories
8. Analysis caching

### Mediano plazo (Próximos 2 meses)
9. Búsqueda full-text
10. Metadata simulaciones
11. Auditoría de cambios

### Largo plazo (Producción)
12. API REST
13. Gemini integration
14. Documentación API
15. CI/CD pipeline

---

## 💡 ALTERNATIVAS Y TRADE-OFFS

### Trade-off 1: Pydantic vs Dataclasses
- ✅ Pydantic: Mejor validación, serialización JSON
- ❌ Pydantic: +1 dependencia

### Trade-off 2: structlog vs logging built-in
- ✅ structlog: Mejor para análisis (JSON)
- ❌ structlog: +1 dependencia

### Trade-off 3: FastAPI vs Flask
- ✅ FastAPI: Auto-generated docs, type hints, async
- ❌ FastAPI: +1 dependencia (pero vale la pena)

### Trade-off 4: Refactor repositories vs dejar como está
- ✅ Refactor: Mantenibilidad, testabilidad
- ❌ Refactor: Requiere cambios en todas las páginas UI

**Recomendación:** Hacer refactor incrementalmente con compatibility layer

---

## 🔗 PRÓXIMOS PASOS

1. **Discutir prioridades** con el equipo
2. **Seleccionar 3-4 mejoras** del Fase 1 para empezar
3. **Crear issues** en GitHub/tracker
4. **Estimar story points** por mejora
5. **Planificar sprints** de 2 semanas

---

**Documento de propuestas finalizado**  
**Listo para revisar e implementar**  
**29 May 2026**
