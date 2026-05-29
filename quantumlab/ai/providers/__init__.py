from quantumlab.ai.providers.base import EmbeddingProvider
from quantumlab.ai.providers.local import LocalEmbeddingProvider


def get_embedding_provider() -> EmbeddingProvider:
    return LocalEmbeddingProvider()
