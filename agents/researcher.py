"""
Researcher Agent - Gathers information from web and local documents
"""

import time
from .base_agent import BaseAgent
from tools.search_tool import WebSearchTool
from tools.document_store import DocumentStore


class ResearcherAgent(BaseAgent):
    """
    The Researcher gathers information from multiple sources:
    1. DuckDuckGo web search
    2. Local document corpus (50 docs)
    
    It then summarizes findings using the LLM.
    """
    
    def __init__(self):
        super().__init__("Researcher")
        self.web_search = WebSearchTool()
        self.doc_store = DocumentStore()
    
    def research(self, question: str, sub_questions: list = None) -> dict:
        """
        Research a topic using all available sources.
        
        Args:
            question: Main research question
            sub_questions: Optional list of sub-questions from Planner
        
        Returns:
            Dictionary with sources, summary, and metadata
        """
        print(f"\n🔍 Researcher: Gathering information...")
        
        all_sources = []
        all_summaries = []
        
        # Research main question
        print(f"   📡 Main question...")
        sources = self._gather_sources(question)
        if sources:
            summary = self._summarize(question, sources)
            all_sources.extend(sources)
            all_summaries.append(summary)
        
        # Research each sub-question
        if sub_questions:
            for i, sq in enumerate(sub_questions, 1):
                print(f"   📡 Sub-question {i}/{len(sub_questions)}...")
                sources = self._gather_sources(sq)
                if sources:
                    summary = self._summarize(sq, sources)
                    all_sources.extend(sources)
                    all_summaries.append(summary)
                time.sleep(0.5)  # Rate limiting
        
        # Create overall summary
        overall = self._synthesize(question, all_summaries)
        
        print(f"   ✅ Total sources: {len(all_sources)}")
        
        return {
            'question': question,
            'sources': all_sources,
            'summary': overall,
            'total_sources': len(all_sources)
        }
    
    