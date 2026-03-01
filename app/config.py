"""
Configuration management.
Environment-based config loading with validation.
Supports Requirements 11.1–11.5.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DatabaseConfig:
    url: str = "postgresql+asyncpg://localhost:5432/llm_gateway"
    pool_size: int = 20
    max_overflow: int = 10


@dataclass
class RedisConfig:
    url: str = "redis://localhost:6379/0"
    cache_ttl: int = 86400  # 24 hours
    max_cache_size_bytes: int = 1_048_576  # 1MB


@dataclass
class ProviderConfig:
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    aws_region: str = "us-east-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""


@dataclass
class RateLimitConfig:
    default_rpm: int = 60
    default_burst: int = 10
    tenant_rpm: int = 600
    global_rpm: int = 10000


@dataclass
class SecurityConfig:
    cors_origins: list = field(default_factory=lambda: ["*"])
    brute_force_enabled: bool = True


@dataclass
class AppConfig:
    """Root application configuration."""
    app_name: str = "Universal LLM Gateway"
    version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000

    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    providers: ProviderConfig = field(default_factory=ProviderConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)


def load_config() -> AppConfig:
    """
    Load configuration from environment variables.

    Environment variables override defaults using the convention:
    GATEWAY_<SECTION>_<FIELD> (e.g., GATEWAY_DATABASE_URL).
    """
    config = AppConfig(
        environment=os.getenv("GATEWAY_ENVIRONMENT", "development"),
        debug=os.getenv("GATEWAY_DEBUG", "false").lower() == "true",
        log_level=os.getenv("GATEWAY_LOG_LEVEL", "INFO"),
        host=os.getenv("GATEWAY_HOST", "0.0.0.0"),
        port=int(os.getenv("GATEWAY_PORT", "8000")),
    )

    config.database.url = os.getenv(
        "GATEWAY_DATABASE_URL", config.database.url
    )
    config.redis.url = os.getenv(
        "GATEWAY_REDIS_URL", config.redis.url
    )
    config.providers.openai_api_key = os.getenv("OPENAI_API_KEY", "")
    config.providers.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
    config.providers.aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

    return config


def validate_config(config: AppConfig) -> list:
    """
    Validate config and return list of warnings.

    Returns:
        List of warning strings (empty = all good).
    """
    warnings = []

    if not config.providers.openai_api_key:
        warnings.append("OPENAI_API_KEY not set — OpenAI provider will be unavailable")
    if not config.providers.anthropic_api_key:
        warnings.append("ANTHROPIC_API_KEY not set — Anthropic provider will be unavailable")
    if config.environment == "production" and config.debug:
        warnings.append("Debug mode is ON in production!")

    return warnings
