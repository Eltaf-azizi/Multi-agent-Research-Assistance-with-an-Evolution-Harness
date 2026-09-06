"""
Writer Agent - Produces the final cited research brief
"""

import re
from .base_agent import BaseAgent


class WriterAgent(BaseAgent):
    """
    The Writer creates a professional, well-structured research brief
    with inline citations to sources.
    
    Output format:
    - Executive Summary
    - Main Findings (with [Source X] citations)
    - Key Facts (bullet points with citations)
    - Sources Used (numbered list)
    """
    
    def __init__(self):
        super().__init__("Writer")
    
    def write_brief(self, research_data: dict) -> str:
        """
        Write a comprehensive research brief.
        
        Args:
            research_data: Dictionary with 'question', 'summary', 'sources'
        
        Returns:
            Formatted brief with citations
        """
        print(f"\n✍️  Writer: Creating brief...")
        
        question = research_data.get('question', '')
        summary = research_data.get('summary', '')
        sources = research_data.get('sources', [])
        
        # Format sources
        sources_text = self._format_sources(sources)
        
        system_prompt = """You are an expert research writer. Create a comprehensive, 
well-cited research brief based on the provided research.

CRITICAL RULES:
1. EVERY factual claim MUST have an inline citation like [1], [2], [3]
2. Never invent facts not in the research data
3. Use formal, academic language
4. Structure your brief EXACTLY as:

EXECUTIVE SUMMARY
(2-3 sentences summarizing the key findings)

MAIN FINDINGS
(2-3 detailed paragraphs, each with multiple citations)

KEY FACTS
• Fact with citation [X]
• Fact with citation [X]
• Fact with citation [X]

SOURCES USED
[1] Source title - Brief description
[2] Source title - Brief description

If research is insufficient on any point, state that clearly."""
        
        user_prompt = f"""Write a research brief answering this question:

QUESTION: {question}

RESEARCH SUMMARY:
{summary}

AVAILABLE SOURCES:
{sources_text}

Write the complete brief following ALL rules above. Every fact MUST have a citation."""
        
        brief = self.call_llm(system_prompt, user_prompt, temperature=0.3)
        
        if brief:
            # Verify citations
            citations = re.findall(r'\[\d+\]', brief)
            if citations:
                print(f"   ✅ {len(set(citations))} unique citations found")
            else:
                print(f"   ⚠️  WARNING: No citations found!")
            
            print(f"   ✅ Brief created ({len(brief)} chars)")
        
        return brief if brief else "Error generating brief."
    
    def _format_sources(self, sources: list) -> str:
        """Format source list for the LLM prompt"""
        if not sources:
            return "No sources available."
        
        text = ""
        for i, s in enumerate(sources, 1):
            text += f"[{i}] {s.get('title', 'Untitled')}\n"
            text += f"    {s.get('snippet', 'No description')[:200]}\n"
            if s.get('url'):
                text += f"    URL: {s.get('url')}\n"
            text += "\n"
        
        return text