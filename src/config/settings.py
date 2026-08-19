"""
Professional settings management with validation
Uses pydantic-settings for type-safe configuration
"""

import os
from pathlib import Path
from typing import Optional, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator


class LLMSettings(BaseSettings):
    """LLM configuration"""
    provider: Literal["groq", "gemini", "ollama"] = "groq"
    model_name: str = "mixtral-8x7b-32768"
    temperature: float = Field(default=0.3, ge=0.0, le=1.0)
    max_tokens: int = Field(default=2000, ge=100, le=8000)
    request_timeout: int = Field(default=30, ge=5, le=120)
    max_retries: int = Field(default=3, ge=1, le=5)


class SearchSettings(BaseSettings):
    """Search configuration"""
    engine: Literal["duckduckgo", "local", "hybrid"] = "duckduckgo"
    num_results: int = Field(default=3, ge=1, le=10)
    timeout: int = Field(default=10, ge=1, le=30)
    rate_limit_delay: float = Field(default=1.0, ge=0.1, le=5.0)


class AgentSettings(BaseSettings):
    """Agent configuration"""
    max_sub_questions: int = Field(default=5, ge=1, le=10)
    enable_critic: bool = False
    enable_cache: bool = True
    cache_ttl_hours: int = Field(default=24, ge=1, le=168)


class EvaluationSettings(BaseSettings):
    """Evaluation configuration"""
    test_set_path: Path = Path("data/evaluation/test_set.json")
    min_pass_score: float = Field(default=60.0, ge=0.0, le=100.0)
    scoring_methods: list[str] = ["keyword", "llm_judge", "factual"]


class PathSettings(BaseSettings):
    """Path configuration"""
    root_dir: Path = Path(__file__).parent.parent.parent
    src_dir: Path = Path(__file__).parent.parent
    data_dir: Path = root_dir / "data"
    logs_dir: Path = root_dir / "logs"
    documents_dir: Path = data_dir / "documents"


class Settings(BaseSettings):
    """Main settings class"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # API Keys
    groq_api_key: Optional[str] = Field(default=None, validation_alias="GROQ_API_KEY")
    gemini_api_key: Optional[str] = Field(default=None, validation_alias="GEMINI_API_KEY")
    
    # Sub-settings
    llm: LLMSettings = LLMSettings()
    search: SearchSettings = SearchSettings()
    agents: AgentSettings = AgentSettings()
    evaluation: EvaluationSettings = EvaluationSettings()
    paths: PathSettings = PathSettings()
    
    # Application
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    
    @validator("groq_api_key")
    def validate_api_key(cls, v):
        """Ensure API key is set for Groq provider"""
        if not v:
            print("⚠️  WARNING: GROQ_API_KEY not set. Create a .env file or set environment variable.")
        return v


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings instance (singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = Settings()
        # Create directories
        _settings.paths.logs_dir.mkdir(parents=True, exist_ok=True)
        _settings.paths.data_dir.mkdir(parents=True, exist_ok=True)
    return _settings