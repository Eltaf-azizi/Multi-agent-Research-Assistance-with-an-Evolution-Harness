"""
Production state management with validation and serialization
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import json
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)


class PipelineStatus(Enum):
    """Pipeline execution status"""
    INITIALIZED = "initialized"
    PLANNING = "planning"
    PLANNED = "planned"
    RESEARCHING = "researching"
    RESEARCHED = "researched"
    WRITING = "writing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ResearchState:
    """
    Immutable-ish state that flows through the pipeline
    
    Features:
    - Type safety with dataclass
    - Automatic serialization
    - Status tracking
    - Execution metrics
    """
    
    # Input
    question: str
    
    # Planner output
    sub_questions: List[str] = field(default_factory=list)
    
    # Researcher output
    search_results: List[Dict[str, Any]] = field(default_factory=list)
    research_summary: str = ""
    
    # Writer output
    brief: str = ""
    
    # Pipeline status
    status: PipelineStatus = PipelineStatus.INITIALIZED
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    # Metrics
    planning_time: float = 0.0
    research_time: float = 0.0
    writing_time: float = 0.0
    
    @property
    def total_time(self) -> float:
        """Calculate total execution time"""
        if self.completed_at:
            return (self.completed_at - self.created_at).total_seconds()
        return 0.0
    
    @property
    def source_count(self) -> int:
        """Number of unique sources"""
        return len(self.search_results)
    
    @property
    def has_citations(self) -> bool:
        """Check if brief contains citations"""
        import re
        return bool(re.search(r'\[(?:Source )?\d+\]', self.brief))
    
    def mark_completed(self):
        """Mark pipeline as completed"""
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
            'question': self.question,
            'sub_questions': self.sub_questions,
            'research_summary': self.research_summary[:500],
            'brief': self.brief,
            'brief_length': len(self.brief),
            'source_count': self.source_count,
            'has_citations': self.has_citations,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'total_time': round(self.total_time, 2),
            'planning_time': round(self.planning_time, 2),
            'research_time': round(self.research_time, 2),
            'writing_time': round(self.writing_time, 2),
            'error': self.error
        }
    
    def save(self, filepath: Optional[Path] = None):
        """Save state to JSON file"""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = Path(f"research_state_{timestamp}.json")
        
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        
        logger.info("State saved", filepath=str(filepath))