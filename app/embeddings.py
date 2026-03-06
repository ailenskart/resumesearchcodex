import hashlib
import math
from functools import lru_cache

from app.config import settings


@lru_cache(maxsize=1)
def _load_sentence_transformer():
    from sentence_transformers import SentenceTransformer  # type: ignore

    return SentenceTransformer("all-MiniLM-L6-v2")


def embed_text(text: str) -> list[float]:
    if settings.embedding_provider.upper() == "LOCAL_SENTENCE_TRANSFORMERS":
        try:
            model = _load_sentence_transformer()
            return model.encode([text])[0].tolist()
        except Exception:
            return hash_embedding(text, settings.embedding_dimension)
    return hash_embedding(text, settings.embedding_dimension)


def hash_embedding(text: str, dim: int) -> list[float]:
    vals = [0.0] * dim
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode()).digest()
        idx = digest[0] % dim
        vals[idx] += 1.0
    norm = math.sqrt(sum(v * v for v in vals)) or 1.0
    return [v / norm for v in vals]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    n = min(len(a), len(b))
    return sum(a[i] * b[i] for i in range(n))
