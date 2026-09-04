"""
BASE_AGENT.PY - Enhanced base agent with logging and metrics
"""

import os
import sys
import time
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class BaseAgent:
    """Enhanced base agent with logging and metrics"""
    
    def __init__(self, name: str):
        self.name = name
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"
        self.temperature = 0.3
        self.max_tokens = 2000
        
        # Metrics tracking
        self.metrics = {
            'total_calls': 0,
            'total_tokens': 0,
            'total_time': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
        
        print(f"✅ {self.name} initialized")
    
    