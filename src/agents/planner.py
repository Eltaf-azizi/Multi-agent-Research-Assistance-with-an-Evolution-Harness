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
