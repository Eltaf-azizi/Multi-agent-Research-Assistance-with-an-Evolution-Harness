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
    
    def _research_node(self, state: ResearchState) -> ResearchState:
        """Research node"""
        if state.status == PipelineStatus.FAILED:
            return state
        
        logger.info("Research phase started")
        state.status = PipelineStatus.RESEARCHING
        
        start = time.time()
        
        try:
            research_data = self.researcher.research(
                state.question,
                state.sub_questions
            )
            
            state.search_results = research_data.get('sources', [])
            state.research_summary = research_data.get('summary', '')
            state.status = PipelineStatus.RESEARCHED
            state.research_time = time.time() - start
            
            logger.info(
                "Research phase completed",
                sources=len(state.search_results),
                time=round(state.research_time, 2)
            )
        except Exception as e:
            logger.error("Research failed", error=str(e))
            state.mark_failed(str(e))
        
        return state
    
    def _write_node(self, state: ResearchState) -> ResearchState:
        """Writing node"""
        if state.status == PipelineStatus.FAILED:
            return state
        
        logger.info("Writing phase started")
        state.status = PipelineStatus.WRITING
        
        start = time.time()
        
        try:
            brief = self.writer.write_brief({
                'question': state.question,
                'summary': state.research_summary,
                'sources': state.search_results
            })
            
            state.brief = brief
            state.writing_time = time.time() - start
            state.mark_completed()
            
            logger.info(
                "Writing phase completed",
                brief_length=len(brief),
                time=round(state.writing_time, 2)
            )
        except Exception as e:
            logger.error("Writing failed", error=str(e))
            state.mark_failed(str(e))
        
        return state
    
    def execute(self, question: str) -> ResearchState:
        """
        Execute the full research pipeline
        
        Args:
            question: The research question
            
        Returns:
            Final ResearchState with results
        """
        
        logger.info("Pipeline execution started", question=question[:100])
        
        initial_state = ResearchState(question=question)
        
        try:
            final_state = self.graph.invoke(initial_state)
            
            logger.info(
                "Pipeline execution completed",
                status=final_state.status.value,
                total_time=round(final_state.total_time, 2)
            )
            
            return final_state
            
        except Exception as e:
            logger.error("Pipeline execution failed", error=str(e))
            initial_state.mark_failed(str(e))
            return initial_state