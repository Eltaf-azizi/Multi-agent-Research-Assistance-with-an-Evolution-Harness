"""
Production Streamlit UI
"""

import streamlit as st
import time
from datetime import datetime

from .config.settings import get_settings
from .config.logging_config import setup_logging
from .orchestration.pipeline import ResearchPipeline

# Page config
st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    .agent-card {
        background: #f0f4ff;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #d0d8ff;
    }
    .citation-badge {
        background: #e8f5e9;
        color: #2e7d32;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_pipeline():
    """Get or create pipeline (cached)"""
    return ResearchPipeline()


def main():
    """Main Streamlit app"""
    
    setup_logging()
    settings = get_settings()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔬 Multi-Agent Research Assistant</h1>
        <p>AI-Powered Research with Source Citations | Production Grade</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        st.subheader("Agents")
        st.markdown("""
        <div class="agent-card">
            <b>📋 Planner</b><br>
            <small>Decomposes questions into sub-tasks</small>
        </div>
        <div class="agent-card">
            <b>🔍 Researcher</b><br>
            <small>Searches web + local documents</small>
        </div>
        <div class="agent-card">
            <b>✍️ Writer</b><br>
            <small>Creates cited research briefs</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.subheader("Settings")
        num_sources = st.slider("Sources per query", 2, 5, 3)
        
        st.markdown("---")
        st.caption(f"v1.0.0 | Model: {settings.llm.model_name}")
    
    # Main content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        question = st.text_input(
            "Enter your research question:",
            placeholder="e.g., What are the latest developments in quantum computing?",
            key="research_input"
        )
        
        research_btn = st.button(
            "🔍 Start Research",
            type="primary",
            use_container_width=True
        )
    
    if research_btn and question:
        pipeline = get_pipeline()
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Execution phases
        phases = [
            ("📋 Planning...", 20),
            ("🔍 Researching...", 60),
            ("✍️ Writing...", 90),
            ("✅ Complete!", 100)
        ]
        
        try:
            for phase_text, progress in phases:
                status_text.info(phase_text)
                progress_bar.progress(progress)
                time.sleep(0.5)
            
            # Execute pipeline
            state = pipeline.execute(question)
            
            if state.status.value == "completed":
                # Display results
                st.markdown("---")
                st.markdown("## 📄 Research Brief")
                st.markdown(state.brief)
                
                # Metrics
                st.markdown("---")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📋 Sub-Questions", len(state.sub_questions))
                with col2:
                    st.metric("📚 Sources", state.source_count)
                with col3:
                    st.metric("⏱️ Total Time", f"{state.total_time:.1f}s")
                with col4:
                    st.metric("✅ Citations", "Yes" if state.has_citations else "No")
                
                # Download
                st.download_button(
                    "📥 Download Brief",
                    state.brief,
                    file_name=f"research_brief_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
            else:
                st.error(f"Research failed: {state.error}")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    elif research_btn:
        st.warning("⚠️ Please enter a question!")


if __name__ == "__main__":
    main()