"""Embeddings.

`HashingEmbedder` is a dependency-free bag-of-words hashing-trick embedder
(stable MD5-based hashing, not Python's randomized built-in `hash()`) so the
repo runs and produces reproducible vectors with zero API keys. It is
explicitly a placeholder for a real embeddings API in production —
`OpenAIEmbedder` / `AnthropicEmbedder`-style adapters would implement the
same `embed(text) -> list[float]` interface against a real model.
"""
from __future__ import annotations

import hashlib
import math
import re
from abc import ABC, abstractmethod

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "to", "of",
    "and", "or", "in", "on", "for", "with", "at", "by", "from", "as", "that",
    "this", "it", "its", "shall", "any", "such", "what", "how",
}


def tokenize(text: str) -> list[str]:
    tokens = _TOKEN_RE.findall(text.lower())
    return [t for t in tokens if t not in _STOPWORDS]


class Embedder(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]: ...


class HashingEmbedder(Embedder):
    def __init__(self, dimensions: int = 128):
        self.dimensions = dimensions

    def _bucket(self, token: str) -> int:
        digest = hashlib.md5(token.encode("utf-8")).hexdigest()
        return int(digest, 16) % self.dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in tokenize(text):
            vector[self._bucket(token)] += 1.0

        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]
