"""
TEST_AGENTS.PY - Unit tests for all agents
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.planner import PlannerAgent
from agents.researcher import ResearcherAgent
from agents.writer import WriterAgent
from tools.search_tool import WebSearchTool

def test_planner():
    """Test planner agent"""
    print("\n🧪 Testing Planner...")
    planner = PlannerAgent()
    
    questions = [
        "What is AI?",
        "How does solar energy work?"
    ]
    
    for q in questions:
        result = planner.create_plan(q)
        assert len(result) > 0, f"No sub-questions for: {q}"
        print(f"✅ {q[:30]}... -> {len(result)} sub-questions")
    
    print("✅ Planner tests passed!")

def test_search():
    """Test search tool"""
    print("\n🧪 Testing Search Tool...")
    searcher = WebSearchTool()
    
    results = searcher.search("Python programming")
    assert len(results) > 0, "No search results"
    print(f"✅ Found {len(results)} results")
    
    print("✅ Search tests passed!")

def test_writer():
    """Test writer agent"""
    print("\n🧪 Testing Writer...")
    writer = WriterAgent()
    
    mock_data = {
        'question': 'What is Python?',
        'summary': 'Python is a programming language.',
        'sources': [
            {'title': 'Source 1', 'snippet': 'Python info...'}
        ]
    }
    
    brief = writer.write_brief(mock_data)
    assert len(brief) > 0, "No brief generated"
    assert '[' in brief, "No citations found"
    print(f"✅ Generated brief with {len(brief)} characters")
    
    print("✅ Writer tests passed!")

def test_integration():
    """Test full pipeline"""
    print("\n🧪 Testing Integration...")
    
    from main import ResearchOrchestrator
    orch = ResearchOrchestrator()
    
    result = orch.research("What is Python?", verbose=False)
    
    assert result['brief'], "No brief generated"
    assert result['sources_count'] > 0, "No sources found"
    print(f"✅ Full pipeline works: {result['sources_count']} sources")
    
    print("✅ Integration tests passed!")

if __name__ == "__main__":
    print("="*60)
    print("🧪 RUNNING ALL TESTS")
    print("="*60)
    
    tests = [
        test_planner,
        test_search,
        test_writer,
        test_integration
    ]
    
    passed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{len(tests)} test suites passed")
    print("="*60)