from abc import ABC, abstractmethod


class SearchBackend(ABC):
    """Abstract interface for search backends."""

    @abstractmethod
    def search(self, query: str) -> list[str]:
        raise NotImplementedError
