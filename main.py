"""
Main entry point - Complete research pipeline
Planner → Researcher → Writer
"""

import time
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from agents.planner import PlannerAgent
from agents.researcher import ResearcherAgent
from agents.writer import WriterAgent
from state_manager import ResearchState
import config


class ResearchOrchestrator:
    """
    Orchestrates the three-agent research pipeline.
    
    Flow:
    1. Planner: Question → Sub-questions
    2. Researcher: Sub-questions → Research data
    3. Writer: Research data → Cited brief
    """
    

    def __init__(self):
        """Initialize all three agents"""
        print("\n" + "=" * 50)
        print("🚀 INITIALIZING RESEARCH SYSTEM")
        print("=" * 50)
        
        # Validate configuration
        if not config.validate():
            print("\n❌ Configuration invalid. Please fix errors above.")
            sys.exit(1)
        
        self.planner = PlannerAgent()
        self.researcher = ResearcherAgent()
        self.writer = WriterAgent()
        
        print("\n✅ All agents ready!")
        print("   Pipeline: Planner → Researcher → Writer\n")
    
    def research(self, question: str, verbose: bool = True) -> dict:
            """
            Execute the complete research pipeline.
            
            Args:
                question: The research question
                verbose: Print detailed progress
            
            Returns:
                Dictionary with all results
            """
            state = ResearchState(question=question)
            
            if verbose:
                print("\n" + "=" * 60)
                print(f"🔬 RESEARCHING: {question}")
                print("=" * 60)
            
            # STEP 1: PLANNING
            if verbose:
                print("\n📋 STEP 1: PLANNING")
                print("-" * 40)
            
            try:
                p_start = time.time()
                state.sub_questions = self.planner.create_plan(question)
                state.planning_time = time.time() - p_start
                state.status = state.status.__class__.PLANNED
            except Exception as e:
                state.mark_failed(f"Planner error: {e}")
                return self._return_result(state, verbose)
            
            