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
    
    