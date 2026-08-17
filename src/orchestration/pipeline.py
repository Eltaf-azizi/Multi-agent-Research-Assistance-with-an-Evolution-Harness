"""
Production pipeline using LangGraph for state management
"""

import time
from typing import Optional
import structlog

from langgraph.graph import StateGraph, END

from ..agents.planner import PlannerAgent
from ..agents.researcher import ResearcherAgent
from ..agents.writer import WriterAgent
from .state import ResearchState, PipelineStatus

logger = structlog.get_logger(__name__)


class ResearchPipeline:
    """
    Production research pipeline with LangGraph orchestration
    
    Features:
    - Graph-based state management
    - Parallel execution where possible
    - Automatic error recovery
    - Comprehensive logging
    - Performance metrics
    """
    
    def __init__(self):
        self.planner = PlannerAgent()
        self.researcher = ResearcherAgent()
        self.writer = WriterAgent()
        self.graph = self._build_graph()
        logger.info("Research pipeline initialized")
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        workflow = StateGraph(ResearchState)
        
        # Add nodes
        workflow.add_node("plan", self._plan_node)
        workflow.add_node("research", self._research_node)
        workflow.add_node("write", self._write_node)
        
        # Define edges
        workflow.set_entry_point("plan")
        workflow.add_edge("plan", "research")
        workflow.add_edge("research", "write")
        workflow.add_edge("write", END)
        
        return workflow.compile()
    
    def _plan_node(self, state: ResearchState) -> ResearchState:
        """Planning node"""
        logger.info("Planning phase started")
        state.status = PipelineStatus.PLANNING
        
        start = time.time()
        
        try:
            sub_questions = self.planner.create_plan(state.question)
            state.sub_questions = sub_questions
            state.status = PipelineStatus.PLANNED
            state.planning_time = time.time() - start
            
            logger.info(
                "Planning phase completed",
                num_questions=len(sub_questions),
                time=round(state.planning_time, 2)
            )
        except Exception as e:
            logger.error("Planning failed", error=str(e))
            state.mark_failed(str(e))
        
        return state
    
    