from abc import ABC, abstractmethod


class VectorStore(ABC):
    @abstractmethod
    def add(self, id: str, vector: list[float], metadata: dict, text: str) -> None: ...

    @abstractmethod
    def query(self, vector: list[float], top_k: int = 5) -> list[dict]:
        """Return up to top_k {id, score, metadata, text} dicts, highest score first."""
