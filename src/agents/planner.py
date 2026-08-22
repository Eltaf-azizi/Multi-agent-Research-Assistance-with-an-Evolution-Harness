"""
Production Planner Agent with JSON parsing and validation
"""

import json
import re
from typing import List, Optional
import structlog

from .base import BaseAgent

logger = structlog.get_logger(__name__)


class PlannerAgent(BaseAgent):
    """
    Strategic planner that decomposes complex questions
    
    Features:
    - Structured JSON output parsing
    - Multiple fallback parsing strategies
    - Question validation
    - Configurable max sub-questions
    """
    
    def __init__(self):
        super().__init__("Planner")
    
    def create_plan(self, question: str) -> List[str]:
        """
        Decompose a research question into sub-questions
        
        Args:
            question: The main research question
            
        Returns:
            List of sub-question strings
            
        Raises:
            ValueError: If question is empty
        """
        
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
        
        logger.info("Creating research plan", question=question[:100])
        
        system_prompt = self._build_system_prompt()
        
        try:
            response = self.call_llm(
                system_prompt=system_prompt,
                user_prompt=question,
                temperature=0.2  # Low temperature for consistent planning
            )
            
            sub_questions = self._parse_response(response)
            
            if sub_questions:
                logger.info(
                    "Plan created successfully",
                    num_questions=len(sub_questions)
                )
                return sub_questions[:self.settings.agents.max_sub_questions]
            else:
                logger.warning("Failed to parse sub-questions, using fallback")
                return [question]
                
        except Exception as e:
            logger.error("Planning failed", error=str(e))
            return [question]
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for planning"""
        return """You are an expert research strategist. Your role is to decompose 
complex research questions into specific, answerable sub-questions.

CRITICAL RULES:
1. Return ONLY a valid JSON array of strings
2. Each sub-question must end with a question mark
3. Cover different aspects of the main question
4. Order from foundational to specific
5. Each question should be independently researchable

EXAMPLE INPUT: "What is the impact of AI on healthcare?"
EXAMPLE OUTPUT: [
    "How is AI currently being used in medical diagnosis?",
    "What are the cost benefits of AI in healthcare systems?",
    "What are the ethical concerns of AI in patient care?",
    "How accurate are AI diagnostic tools compared to human doctors?",
    "What is the future outlook for AI in healthcare?"
]

Now decompose the following question:"""
    
    def _parse_response(self, response: str) -> Optional[List[str]]:
        """
        Parse LLM response with multiple strategies
        
        Strategy 1: Parse as valid JSON
        Strategy 2: Extract JSON array from text
        Strategy 3: Extract question-mark lines
        Strategy 4: Split by question marks
        """
        
        # Strategy 1: Direct JSON parse
        try:
            questions = json.loads(response)
            if isinstance(questions, list):
                return self._clean_questions(questions)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Extract JSON array
        try:
            json_match = re.search(r'\[.*?\]', response, re.DOTALL)
            if json_match:
                questions = json.loads(json_match.group())
                if isinstance(questions, list):
                    return self._clean_questions(questions)
        except:
            pass
        
        # Strategy 3: Line-by-line extraction
        questions = []
        for line in response.split('\n'):
            cleaned = re.sub(r'^[\d.\-•*"\'\s\[\]]+', '', line.strip())
            if '?' in cleaned and len(cleaned) > 10:
                questions.append(cleaned)
        
        if questions:
            return questions
        
        # Strategy 4: Split by question marks
        parts = response.split('?')
        questions = [p.strip() + '?' for p in parts if len(p.strip()) > 5]
        
        return questions if questions else None
    
    def _clean_questions(self, questions: List[str]) -> List[str]:
        """Clean and validate questions"""
        cleaned = []
        for q in questions:
            if isinstance(q, str):
                q = q.strip().strip('"\'').strip()
                if len(q) > 10:
                    if not q.endswith('?'):
                        q += '?'
                    cleaned.append(q)
        return cleaned