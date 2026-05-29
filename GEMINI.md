# QuantumLab Project Context

Este proyecto es un laboratorio de exploración científica y filosófica.

OBJETIVO:
Convertir hipótesis en simulaciones, experimentos y análisis matemáticos.

MÓDULOS CORE:
- Hypothesis System (SQLite)
- Reality Engine (simulaciones físicas)
- Graph Connections (network de ideas)
- Hypothesis Analyzer (análisis semántico con embeddings)
- Experiment Generator / Reality Engine
- Future: Gemini API integration

ARQUITECTURA:
→ Ver ARCHITECTURE.md para diagrama completo
  ├─ 3 capas: UI (Streamlit) → Lógica → Datos (SQLite)
  ├─ 5 módulos core + subsistema AI
  ├─ 6 páginas especializadas
  └─ 4 tipos de simulaciones

REGLAS:
- No romper arquitectura modular
- No reescribir todo el proyecto sin permiso
- Mantener compatibilidad entre módulos
- Preferir expansión incremental
- Preservar separación de concerns

STACK:
- Python 3.11+
- Streamlit (UI)
- SQLite (persistent storage)
- NetworkX (graph algorithms)
- NumPy / SciPy (numerical computing)
- Plotly (interactive viz)
- sentence-transformers (embeddings, optional)

PUNTOS CRÍTICOS DETECTADOS:
⚠️  Sin tests (0% coverage)
⚠️  Validación insuficiente en entrada
⚠️  Sin índices en BD (performance issue)
⚠️  Dos sistemas de similitud competidores
⚠️  Análisis no persistente
⚠️  Sin logging centralizado
⚠️  Sin auditoría de cambios

FORTALEZAS:
✅ Arquitectura modular clara
✅ Resilencia de IA (fallback automático)
✅ Seguridad en expresiones (AST whitelist)
✅ Análisis avanzado (8 tipos)
✅ Completamente local (offline-first)
✅ Visualización interactiva de grafos