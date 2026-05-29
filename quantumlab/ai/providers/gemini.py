from __future__ import annotations

from quantumlab.ai.config import AI_CONFIG


class GeminiProvider:
    """Future Gemini API integration point.

    External calls are intentionally disabled unless QUANTUMLAB_ENABLE_EXTERNAL_AI=1.
    The local analyzer does not depend on this provider.
    """

    name = "Gemini Provider"

    def is_configured(self) -> bool:
        return bool(AI_CONFIG.gemini_api_key and AI_CONFIG.enable_external_calls)

    def analyze(self, prompt: str) -> str:
        raise NotImplementedError("Gemini API integration is prepared but not enabled yet.")
