"""
Abstract base agent with production features:
- Retry logic with exponential backoff
- Request timeouts
- Metrics collection
- Structured logging
"""

import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from groq import Groq, APIError, RateLimitError, APITimeoutError

from ..config.settings import get_settings

logger = structlog.get_logger(__name__)


@dataclass
class AgentMetrics:
    """Track agent performance"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_tokens: int = 0
    total_time: float = 0.0
    errors: Dict[str, int] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    
    @property
    def success_rate(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return (self.successful_calls / self.total_calls) * 100
    
    @property
    def avg_response_time(self) -> float:
        if self.successful_calls == 0:
            return 0.0
        return self.total_time / self.successful_calls


class BaseAgent(ABC):
    """
    Abstract base agent with production-grade features
    
    Features:
    - Automatic retries for transient failures
    - Request timeout handling
    - Metrics collection
    - Structured logging
    - Type-safe configuration
    """
    
    def __init__(self, name: str):
        self.name = name
        self.settings = get_settings()
        self.logger = logger.bind(agent=name)
        
        # Initialize LLM client
        self.client = self._create_client()
        
        # Metrics
        self.metrics = AgentMetrics()
        
        self.logger.info(f"Agent initialized", model=self.settings.llm.model_name)
    
    def _create_client(self) -> Groq:
        """Create and validate LLM client"""
        api_key = self.settings.groq_api_key
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not set. Create a .env file or set environment variable."
            )
        return Groq(api_key=api_key)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((RateLimitError, APITimeoutError))
    )
    def call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Make a production-grade LLM call with retries and error handling
        
        Args:
            system_prompt: System-level instructions
            user_prompt: User query or data
            temperature: Override default temperature
            max_tokens: Override default max tokens
        
        Returns:
            LLM response text
        
        Raises:
            ValueError: If prompts are empty
            RuntimeError: If all retries fail
        """
        
        if not system_prompt or not user_prompt:
            raise ValueError("System and user prompts cannot be empty")
        
        temp = temperature or self.settings.llm.temperature
        tokens = max_tokens or self.settings.llm.max_tokens
        
        self.logger.debug(
            "LLM call started",
            system_prompt_len=len(system_prompt),
            user_prompt_len=len(user_prompt),
            temperature=temp
        )
        
        start_time = time.time()
        self.metrics.total_calls += 1
        
        try:
            response = self.client.chat.completions.create(
                model=self.settings.llm.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temp,
                max_tokens=tokens,
                timeout=self.settings.llm.request_timeout
            )
            
            result = response.choices[0].message.content
            
            # Update metrics
            elapsed = time.time() - start_time
            self.metrics.successful_calls += 1
            self.metrics.total_time += elapsed
            
            if hasattr(response, 'usage'):
                self.metrics.total_tokens += response.usage.total_tokens
            
            self.logger.info(
                "LLM call succeeded",
                response_len=len(result),
                time_seconds=round(elapsed, 2),
                tokens=response.usage.total_tokens if hasattr(response, 'usage') else None
            )
            
            return result
            
        except RateLimitError as e:
            self.metrics.failed_calls += 1
            self.metrics.errors['rate_limit'] = self.metrics.errors.get('rate_limit', 0) + 1
            self.logger.warning("Rate limit hit, retrying...", error=str(e))
            raise  # Let tenacity handle retry
            
        except APITimeoutError as e:
            self.metrics.failed_calls += 1
            self.metrics.errors['timeout'] = self.metrics.errors.get('timeout', 0) + 1
            self.logger.warning("Request timed out, retrying...", error=str(e))
            raise
            
        except APIError as e:
            self.metrics.failed_calls += 1
            self.metrics.errors['api_error'] = self.metrics.errors.get('api_error', 0) + 1
            self.logger.error("API error", error=str(e))
            raise RuntimeError(f"API error after retries: {e}")
            
        except Exception as e:
            self.metrics.failed_calls += 1
            self.metrics.errors['unknown'] = self.metrics.errors.get('unknown', 0) + 1
            self.logger.error("Unexpected error", error=str(e))
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        return {
            'name': self.name,
            'total_calls': self.metrics.total_calls,
            'success_rate': f"{self.metrics.success_rate:.1f}%",
            'avg_response_time': f"{self.metrics.avg_response_time:.2f}s",
            'total_tokens': self.metrics.total_tokens,
            'errors': self.metrics.errors,
            'uptime_seconds': (datetime.now() - self.metrics.start_time).total_seconds()
        }