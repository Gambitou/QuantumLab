from __future__ import annotations

import hashlib
import re
import unicodedata

import numpy as np

from quantumlab.ai.config import AI_CONFIG


class LocalEmbeddingProvider:
    name = "Local Embedding Provider"

    def __init__(self) -> None:
        self.mode = "hashed-text"
        self._model = None
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(AI_CONFIG.local_embedding_model, device="cpu")
            self.mode = "sentence-transformers"
        except Exception:
            self._model = None

    def encode(self, texts: list[str]) -> np.ndarray:
        if self._model is not None:
            vectors = self._model.encode(
                texts,
                batch_size=16,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            return np.asarray(vectors, dtype=float)
        return self._hashed_embeddings(texts)

    def _hashed_embeddings(self, texts: list[str], dimensions: int = 256) -> np.ndarray:
        vectors = np.zeros((len(texts), dimensions), dtype=float)
        for row, text in enumerate(texts):
            for token in _tokens(text):
                digest = hashlib.blake2b(token.encode("utf-8"), digest_size=4).digest()
                index = int.from_bytes(digest[:2], "little") % dimensions
                sign = 1.0 if digest[2] % 2 == 0 else -1.0
                vectors[row, index] += sign

        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return vectors / norms


def _tokens(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKD", text.lower())
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return [token for token in re.findall(r"[a-z0-9]+", ascii_text) if len(token) > 2]
