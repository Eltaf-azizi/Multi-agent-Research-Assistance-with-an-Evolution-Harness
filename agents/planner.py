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

CRITICAL RULES:
1. Return ONLY a valid JSON array of strings
2. Each sub-question must be a complete question ending with ?
3. Questions should cover different aspects of the main topic
4. Order from foundational/basic to specific/complex
5. Each question must be independently researchable

EXAMPLE:
Input: "What is the impact of social media on mental health?"
Output: [
    "What percentage of people use social media daily?",
    "What are the documented psychological effects of social media use?",
    "How does social media affect sleep patterns and anxiety levels?",
    "What age groups are most vulnerable to social media's negative effects?",
    "What strategies do experts recommend for healthy social media use?"
]

Return ONLY the JSON array, nothing else."""
        
        response = self.call_llm(system_prompt, question, temperature=0.2)
        
        sub_questions = self._parse_response(response)
        
        if sub_questions:
            print(f"   ✅ Created {len(sub_questions)} sub-questions:")
            for i, q in enumerate(sub_questions, 1):
                print(f"      {i}. {q}")
            return sub_questions[:5]
        else:
            print(f"   ⚠️  Could not parse sub-questions, using main question only")
            return [question]
    
    def _parse_response(self, response: str) -> list:
        """Parse the LLM response to extract questions"""
        
        # Method 1: Try to parse as JSON
        try:
            json_match = re.search(r'\[.*?\]', response, re.DOTALL)
            if json_match:
                questions = json.loads(json_match.group())
                if isinstance(questions, list):
                    return [q for q in questions if isinstance(q, str) and len(q) > 10]
        except:
            pass
        
        # Method 2: Extract lines with question marks
        lines = response.split('\n')
        questions = []
        for line in lines:
            cleaned = line.strip().lstrip('0123456789.-•*"\'[]() ')
            if '?' in cleaned and len(cleaned) > 10:
                questions.append(cleaned)
        
        return questions[:5]