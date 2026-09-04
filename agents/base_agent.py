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
    
     def call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Make LLM call with full error handling and metrics"""
        
        start = time.time()
        self.metrics['total_calls'] += 1
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            result = response.choices[0].message.content
            
            # Update metrics
            elapsed = time.time() - start
            self.metrics['total_time'] += elapsed
            
            if hasattr(response, 'usage'):
                tokens = response.usage.total_tokens
                self.metrics['total_tokens'] += tokens
            
            return result
            
        except Exception as e:
            self.metrics['errors'] += 1
            print(f"❌ {self.name} error: {e}")
            return f"Error: {str(e)}"
    
    def get_metrics(self) -> dict:
        """Return performance metrics"""
        runtime = (datetime.now() - self.metrics['start_time']).total_seconds()
        
        return {
            'name': self.name,
            'total_calls': self.metrics['total_calls'],
            'total_tokens': self.metrics['total_tokens'],
            'total_time': round(self.metrics['total_time'], 2),
            'errors': self.metrics['errors'],
            'runtime_seconds': round(runtime, 2),
            'avg_response_time': round(
                self.metrics['total_time'] / max(1, self.metrics['total_calls']), 2
            )
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Timestamped logging"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
        icon = icons.get(level, "📝")
        print(f"[{timestamp}] {icon} {self.name}: {message}")