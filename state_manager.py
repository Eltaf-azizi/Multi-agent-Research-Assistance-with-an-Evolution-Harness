"""
State management with LangGraph integration
"""

from typing import TypedDict, List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class PipelineStatus(Enum):
    """Pipeline execution status"""
    INITIALIZED = "initialized"
    PLANNED = "planned"
    RESEARCHED = "researched"
    WRITTEN = "written"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ResearchState:
    """
    Complete state that flows through the pipeline
    
    This is the "shared memory" between all agents.
    Each agent reads from and writes to this state.
    """
    
    # Input
    question: str = ""
    
    # Planner output
    sub_questions: List[str] = field(default_factory=list)
    
    # Researcher output
    search_results: List[Dict[str, str]] = field(default_factory=list)
    research_summary: str = ""
    
    # Writer output
    brief: str = ""
    
    # Pipeline status
    status: PipelineStatus = PipelineStatus.INITIALIZED
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    # Timing
    planning_time: float = 0.0
    research_time: float = 0.0
    writing_time: float = 0.0
    
    