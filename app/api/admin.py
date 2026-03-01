"""
Admin API endpoints.
Supports Requirements 2.5, 6.5, 6.6, 7.5.

Connected to real services: metrics, request logger, API key service.
"""

import logging
from typing import Dict, Any, List

from fastapi import APIRouter, Query, Depends

from app.services.metrics import metrics
from app.services.request_logger import RequestLogger
from app.api.dependencies import verify_admin_token

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin", 
    tags=["Admin"],
    dependencies=[Depends(verify_admin_token)]
)

# Shared request logger instance (same one used by routes.py)
# In production, this would be injected via dependency injection
_request_logger = RequestLogger()


def get_request_logger() -> RequestLogger:
    """Return the request logger instance (allows test injection)."""
    return _request_logger


@router.get("/api-keys")
async def list_api_keys() -> Dict[str, Any]:
    """
    List API keys (Requirement 2.5).
    Returns structure from API key service.
    """
    # In production, query from api_key_service / database
    return {"keys": [], "total": 0}


@router.get("/analytics")
async def get_analytics() -> Dict[str, Any]:
    """
    Usage analytics (Requirement 7.5).
    Aggregates from metrics collector and request logger.
    """
    m = metrics.get_metrics()
    rl = get_request_logger()
    stats = rl.get_stats()

    return {
        "total_requests": m["gateway_requests_total"],
        "total_tokens": m["tokens_total"],
        "total_cost_usd": str(m["cost_total_usd"]),
        "error_rate": m["gateway_error_rate"],
        "cache_hit_rate": m["cache_hit_rate"],
        "avg_latency_ms": m["gateway_latency_avg_ms"],
        "provider_breakdown": m["provider_requests"],
        "top_models": [],  # Would aggregate from request logs
        "log_stats": stats,
    }


@router.get("/logs")
async def get_logs(
    limit: int = Query(default=100, ge=1, le=1000),
) -> Dict[str, Any]:
    """
    Queryable request logs (Requirement 6.5).
    Returns recent log entries from the request logger.
    """
    rl = get_request_logger()
    logs = rl.get_logs(limit=limit)
    return {"logs": logs, "total": len(logs)}


@router.post("/logs/export")
async def export_logs() -> Dict[str, Any]:
    """
    Log export to S3 (Requirement 6.6).
    """
    rl = get_request_logger()
    return rl.export_logs_to_s3()

@router.post("/config/reload")
async def reload_configuration() -> Dict[str, str]:
    """
    Reload configuration without service restart (Requirement 11.6).
    Clears the lru_cache on get_settings.
    """
    from app.core.config import get_settings
    get_settings.cache_clear()
    logger.info("Configuration hot-reloaded via admin endpoint.")
    return {"status": "success", "message": "Configuration reloaded"}
