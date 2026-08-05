"""
Streamlit Web UI for the Multi-Agent Research Assistant
"""

import streamlit as st
import time
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from main import ResearchOrchestrator

# Page config
st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 Multi-Agent Research Assistant")
st.markdown("### AI-Powered Research with Source Citations")

# Initialize orchestrator
@st.cache_resource
def get_orchestrator():
    return ResearchOrchestrator()

# Sidebar
with st.sidebar:
    st.header("⚙️ About")
    st.markdown("""
    **Three AI Agents:**
    - 📋 **Planner** - Breaks down questions
    - 🔍 **Researcher** - Searches web & documents
    - ✍️ **Writer** - Creates cited briefs
    
    **Features:**
    - Web search (DuckDuckGo)
    - Local document search
    - Source citations
    - 20-question evaluation
    """)

# Main input
question = st.text_input(
    "Enter your research question:",
    placeholder="e.g., What is quantum computing and how does it work?"
)

if st.button("🔍 Research", type="primary"):
    if question:
        orchestrator = get_orchestrator()
        
        with st.spinner("Researching..."):
            result = orchestrator.research(question, verbose=False)
        
        if result['status'] == 'completed':
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📋 Sub-Questions", len(result.get('sub_questions', [])))
            col2.metric("📚 Sources", result.get('sources_count', 0))
            col3.metric("⏱️ Time", f"{result.get('time', 0):.1f}s")
            col4.metric("✅ Citations", "Yes" if result.get('has_citations') else "No")
            
            # Brief
            st.markdown("## 📄 Research Brief")
            st.markdown(result['brief'])
            
            # Download
            st.download_button(
                "📥 Download Brief",
                result['brief'],
                file_name="research_brief.md",
                mime="text/markdown"
            )
        else:
            st.error(f"Research failed: {result.get('status')}")
    else:
        st.warning("Please enter a question!")