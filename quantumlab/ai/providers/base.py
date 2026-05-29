from __future__ import annotations

from typing import Protocol

import numpy as np


class EmbeddingProvider(Protocol):
    name: str
    mode: str

    def encode(self, texts: list[str]) -> np.ndarray:
        """Return one vector per text."""
