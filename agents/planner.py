"""
Planner Agent - Breaks complex questions into sub-questions
"""

import json
import re
from .base_agent import BaseAgent


class PlannerAgent(BaseAgent):
    """
    The Planner decomposes a complex research question into
    3-5 specific, searchable sub-questions.
    
    Input: "What are the effects of AI on healthcare?"
    Output: [
        "How is AI currently used in medical diagnosis?",
        "What are the cost benefits of AI in healthcare?",
        "What are the risks of AI in patient care?"
    ]
    """
    
    def __init__(self):
        super().__init__("Planner")
    
    def create_plan(self, question: str) -> list:
        """
        Decompose a research question into sub-questions.
        
        Args:
            question: The main research question
        
        Returns:
            List of sub-question strings
        """
        print(f"\n📋 Planner: Analyzing question...")
        
        system_prompt = """You are a research planning expert. Your task is to break down 
a complex research question into 3-5 specific, focused sub-questions.

