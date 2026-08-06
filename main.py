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
    
    