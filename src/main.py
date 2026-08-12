"""
Production CLI entry point with rich interface
"""

import sys
import time
from pathlib import Path

import structlog

from .config.settings import get_settings
from .config.logging_config import setup_logging
from .orchestration.pipeline import ResearchPipeline

logger = structlog.get_logger(__name__)


def display_banner():
    """Display application banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     🔬 MULTI-AGENT RESEARCH ASSISTANT v1.0.0                ║
║                                                              ║
║     Production-Grade Pipeline                               ║
║     Planner → Researcher → Writer                           ║
║     With Source Citations & Evaluation                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)


def display_metrics(state):
    """Display execution metrics"""
    print("\n" + "="*60)
    print("📊 EXECUTION METRICS")
    print("="*60)
    print(f"  Status:        {state.status.value}")
    print(f"  Total Time:    {state.total_time:.2f}s")
    print(f"  Planning:      {state.planning_time:.2f}s")
    print(f"  Research:      {state.research_time:.2f}s")
    print(f"  Writing:       {state.writing_time:.2f}s")
    print(f"  Sources:       {state.source_count}")
    print(f"  Sub-questions: {len(state.sub_questions)}")
    print(f"  Citations:     {'✅ Yes' if state.has_citations else '❌ No'}")
    print("="*60)

