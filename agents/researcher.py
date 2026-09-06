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

    
    def _gather_sources(self, query: str) -> list:
        """Gather from both web and local documents"""
        sources = []
        
        # Search web
        web_results = self.web_search.search(query, num_results=2)
        sources.extend(web_results)
        
        # Search local documents
        local_results = self.doc_store.search(query, num_results=1)
        sources.extend(local_results)
        
        return sources
    
    def _summarize(self, question: str, sources: list) -> str:
        """Summarize search results for a single question"""
        if not sources:
            return ""
        
        # Format sources
        source_text = ""
        for i, s in enumerate(sources, 1):
            source_text += f"[{i}] {s.get('title', 'Untitled')}\n"
            source_text += f"    {s.get('snippet', '')[:300]}\n\n"
        
        system_prompt = """Summarize these search results in 2-3 factual sentences.
Include source citations like [1], [2]. Be precise and factual."""
        
        user_prompt = f"Question: {question}\n\nSources:\n{source_text}"
        
        return self.call_llm(system_prompt, user_prompt)
    
    def _synthesize(self, question: str, summaries: list) -> str:
        """Combine all summaries into one comprehensive overview"""
        if not summaries:
            return "No research data available."
        
        combined = "\n\n".join([s for s in summaries if s])
        
        system_prompt = """Synthesize these research summaries into one comprehensive overview.
Keep all source citations. Be factual and thorough."""
        
        user_prompt = f"Main Question: {question}\n\nResearch Summaries:\n{combined}"
        
        return self.call_llm(system_prompt, user_prompt)