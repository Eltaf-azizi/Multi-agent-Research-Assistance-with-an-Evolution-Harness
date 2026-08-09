"""
Local document search for the 50 document corpus
"""

from pathlib import Path
from typing import List, Dict


class DocumentStore:
    """
    Search through local documents.
    Used as an alternative or supplement to web search.
    """
    
    def __init__(self, docs_path: str = "data/documents"):
        self.docs_path = Path(docs_path)
        self.docs_path.mkdir(parents=True, exist_ok=True)
        self.documents = self._load_documents()
        print(f"📚 DocumentStore: {len(self.documents)} documents loaded")
    
    def _load_documents(self) -> List[Dict]:
        """Load all text documents from the docs folder"""
        documents = []
        
        for file_path in self.docs_path.glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                documents.append({
                    'title': file_path.stem.replace('_', ' ').title(),
                    'filename': file_path.name,
                    'content': content,
                    'path': str(file_path)
                })
            except Exception as e:
                print(f"   ⚠️  Could not load {file_path}: {e}")
        
        return documents
    
    def search(self, query: str, num_results: int = 3) -> List[Dict[str, str]]:
        """
        Search local documents for a query.
        
        Args:
            query: Search query
            num_results: Max results to return
        
        Returns:
            List of matching document snippets
        """
        query_lower = query.lower()
        results = []
        
        for doc in self.documents:
            content_lower = doc['content'].lower()
            
            if query_lower in content_lower:
                # Find the relevant section
                idx = content_lower.find(query_lower)
                start = max(0, idx - 100)
                end = min(len(doc['content']), idx + 300)
                snippet = doc['content'][start:end]
                
                results.append({
                    'title': doc['title'],
                    'url': doc['path'],
                    'snippet': f"...{snippet}...",
                    'source': 'local'
                })
                
                if len(results) >= num_results:
                    break
        
        return results