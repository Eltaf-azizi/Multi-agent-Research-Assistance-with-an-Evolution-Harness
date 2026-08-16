from pathlib import Path

from src.tools.search.base import SearchBackend


class LocalDocumentSearch(SearchBackend):
    def __init__(self, documents_dir: str | None = None) -> None:
        self.documents_dir = Path(documents_dir or "data/documents")

    def search(self, query: str) -> list[str]:
        matches = []
        if self.documents_dir.exists():
            for path in self.documents_dir.glob("*.txt"):
                text = path.read_text(encoding="utf-8", errors="ignore")
                if query.lower() in text.lower():
                    matches.append(str(path))
        return matches
