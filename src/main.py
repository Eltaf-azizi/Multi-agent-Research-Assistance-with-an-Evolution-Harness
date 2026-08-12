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


def interactive_mode():
    """Run in interactive CLI mode"""
    setup_logging()
    settings = get_settings()
    
    if not settings.groq_api_key:
        print("\n❌ ERROR: GROQ_API_KEY not set!")
        print("Create a .env file with: GROQ_API_KEY=your_key_here")
        sys.exit(1)
    
    display_banner()
    
    pipeline = ResearchPipeline()
    
    while True:
            print("\n" + "-"*60)
            question = input("\n🔍 Enter research question (or 'quit'/'exit' to stop): ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not question:
                print("⚠️  Please enter a question.")
                continue
            
            print(f"\n🔬 Researching: {question}")
            print("="*60)
            
            try:
                state = pipeline.execute(question)
                
                if state.status.value == "completed":
                    print("\n" + "="*60)
                    print("📄 RESEARCH BRIEF")
                    print("="*60)
                    print(state.brief)
                    print("="*60)
                    
                    display_metrics(state)
                    
                    # Save option
                    save = input("\n💾 Save brief to file? (y/n): ").strip().lower()
                    if save == 'y':
                        state.save()
                else:
                    print(f"\n❌ Research failed: {state.error}")
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted. Goodbye!")
                break
            except Exception as e:
                logger.error("Unexpected error", error=str(e))
                print(f"\n❌ Error: {e}")
    
    
    def main():
        """Main entry point"""
        interactive_mode()
    
    
    if __name__ == "__main__":
        main()