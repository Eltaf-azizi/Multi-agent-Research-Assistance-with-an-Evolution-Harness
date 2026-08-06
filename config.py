"""
CONFIG.PY - Central Configuration
Complete version with all settings
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment
load_dotenv()

# ============================================
# PROJECT PATHS
# ============================================
ROOT_DIR = Path(__file__).parent
AGENTS_DIR = ROOT_DIR / "agents"
TOOLS_DIR = ROOT_DIR / "tools"
EVAL_DIR = ROOT_DIR / "evaluation"
DOCS_DIR = ROOT_DIR / "documents"

# ============================================
# LLM CONFIGURATION
# ============================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.3-70b-versatile"
TEMPERATURE = 0.3
MAX_TOKENS = 2000

# ============================================
# SEARCH CONFIGURATION
# ============================================
SEARCH_ENGINE = "duckduckgo"  # or "local"
NUM_SEARCH_RESULTS = 3
SEARCH_TIMEOUT = 10  # seconds
SEARCH_DELAY = 1     # seconds between searches

# ============================================
# AGENT CONFIGURATION
# ============================================
MAX_SUB_QUESTIONS = 5
ENABLE_CRITIC = False  # Stretch goal
ENABLE_CACHE = True

# ============================================
# EVALUATION CONFIGURATION
# ============================================
TEST_SET_SIZE = 20
SCORING_METHODS = ["keyword", "llm_judge"]

# ============================================
# STREAMLIT CONFIGURATION
# ============================================
STREAMLIT_TITLE = "Multi-Agent Research Assistant"
STREAMLIT_PORT = 8501

# ============================================
# VALIDATION
# ============================================
def validate():
    """Check configuration"""
    print("🔍 Validating configuration...")
    
    checks = []
    
    # Check API key
    if GROQ_API_KEY:
        checks.append(("✅", "API Key loaded"))
    else:
        checks.append(("❌", "API Key missing"))
    
    # Check directories
    for dir_path in [AGENTS_DIR, TOOLS_DIR, EVAL_DIR]:
        if dir_path.exists():
            checks.append(("✅", f"Directory exists: {dir_path.name}"))
        else:
            checks.append(("❌", f"Directory missing: {dir_path.name}"))
    
    # Check documents
    if DOCS_DIR.exists():
        doc_count = len(list(DOCS_DIR.glob("*.txt")))
        checks.append(("✅" if doc_count >= 50 else "⚠️", f"Documents: {doc_count}"))
    
    # Print results
    for status, message in checks:
        print(f"   {status} {message}")
    
    return all(s[0] == "✅" for s in checks)

if __name__ == "__main__":
    validate()