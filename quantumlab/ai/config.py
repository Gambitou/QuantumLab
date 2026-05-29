from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AIProviderConfig:
    provider: str = os.getenv("QUANTUMLAB_AI_PROVIDER", "local")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    local_embedding_model: str = os.getenv(
        "QUANTUMLAB_EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",
    )
    enable_external_calls: bool = os.getenv("QUANTUMLAB_ENABLE_EXTERNAL_AI", "0") == "1"


AI_CONFIG = AIProviderConfig()
