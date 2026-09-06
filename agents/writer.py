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

