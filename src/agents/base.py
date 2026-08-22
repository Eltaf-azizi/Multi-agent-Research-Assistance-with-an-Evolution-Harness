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

