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
    
    
    @property
    def total_time(self) -> float:
        """Total execution time in seconds"""
        if self.completed_at:
            return (self.completed_at - self.created_at).total_seconds()
        return 0.0
    
    @property
    def source_count(self) -> int:
        """Number of sources found"""
        return len(self.search_results)
    
    @property
    def has_citations(self) -> bool:
        """Check if brief contains citations"""
        import re
        return bool(re.search(r'\[\d+\]', self.brief))
    
    def mark_completed(self):
        """Mark pipeline as successfully completed"""
        self.status = PipelineStatus.COMPLETED
        self.completed_at = datetime.now()
    
    def mark_failed(self, error: str):
        """Mark pipeline as failed"""
        self.status = PipelineStatus.FAILED
        self.error = error
        self.completed_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "question": self.question,
            "sub_questions": self.sub_questions,
            "source_count": self.source_count,
            "brief_preview": self.brief[:200] + "..." if len(self.brief) > 200 else self.brief,
            "brief_length": len(self.brief),
            "has_citations": self.has_citations,
            "status": self.status.value,
            "total_time": round(self.total_time, 2),
            "planning_time": round(self.planning_time, 2),
            "research_time": round(self.research_time, 2),
            "writing_time": round(self.writing_time, 2),
            "error": self.error
        }
    
    def save(self, filepath: str = None):
        """Save state to JSON file"""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"research_state_{timestamp}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
        
        print(f"💾 State saved to {filepath}")
    
    def print_summary(self):
        """Print formatted summary"""
        print("\n" + "=" * 60)
        print("📊 RESEARCH STATE SUMMARY")
        print("=" * 60)
        print(f"  Question:       {self.question[:80]}")
        print(f"  Status:         {self.status.value}")
        print(f"  Sub-questions:  {len(self.sub_questions)}")
        print(f"  Sources:        {self.source_count}")
        print(f"  Brief length:   {len(self.brief)} chars")
        print(f"  Has citations:  {'✅' if self.has_citations else '❌'}")
        print(f"  Total time:     {self.total_time:.2f}s")
        print(f"  Planning:       {self.planning_time:.2f}s")
        print(f"  Research:       {self.research_time:.2f}s")
        print(f"  Writing:        {self.writing_time:.2f}s")
        if self.error:
            print(f"  Error:          {self.error}")
        print("=" * 60)