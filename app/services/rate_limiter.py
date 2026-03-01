"""
Token bucket rate limiter backed by Redis.
Supports Requirements 7.1, 7.2, 7.3, 7.4, 7.6, 7.7.

Three tiers of rate limiting:
  1. Per-API-key  — configurable requests per minute (token bucket)
  2. Per-tenant   — aggregate limit across all keys of a tenant
  3. Global       — system-wide throttle (safety net)
"""

import logging
import time
from dataclasses import dataclass
from typing import Optional

from app.cache.redis import RedisManager, redis_manager

logger = logging.getLogger(__name__)

# Redis key prefixes
KEY_PREFIX = "rate_limit"
TENANT_PREFIX = "rate_limit:tenant"
GLOBAL_KEY = "rate_limit:global"

# Defaults
DEFAULT_RPM = 60          # requests per minute
DEFAULT_BURST = 10        # extra burst tokens above steady rate
DEFAULT_TENANT_RPM = 600  # aggregate per-tenant
DEFAULT_GLOBAL_RPM = 5000 # system-wide


@dataclass
class RateLimitResult:
    """Outcome of a rate limit check."""
    allowed: bool
    limit: int
    remaining: int
    reset_at: float          # Unix timestamp when the bucket refills
    retry_after: Optional[int] = None  # seconds to wait (only when denied)


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter using Redis for distributed state.

    Each bucket is keyed by ``rate_limit:{api_key_id}:tokens`` and stores:
      - ``tokens``  – current token count (float, stored as string)
      - ``last``    – last refill timestamp

    Tokens are refilled lazily on each request at a rate of
    ``rate / 60`` tokens per second, capped at ``capacity``.
    """

    def __init__(self, redis: Optional[RedisManager] = None):
        self._redis = redis or redis_manager

    # ------------------------------------------------------------------
    # Per-API-key check  (Requirement 7.1, 7.4)
    # ------------------------------------------------------------------

    async def check_rate_limit(
        self,
        api_key_id: str,
        rate_per_minute: int = DEFAULT_RPM,
        burst: int = DEFAULT_BURST,
    ) -> RateLimitResult:
        """
        Consume one token from the bucket for *api_key_id*.

        Args:
            api_key_id: Unique key identifier.
            rate_per_minute: Steady-state tokens generated per minute.
            burst: Extra tokens above the steady rate (capacity = rate + burst).

        Returns:
            :class:`RateLimitResult` with allow/deny and header values.
        """
        bucket_key = f"{KEY_PREFIX}:{api_key_id}:tokens"
        capacity = rate_per_minute + burst
        refill_rate = rate_per_minute / 60.0  # tokens per second

        return await self._consume_token(bucket_key, capacity, refill_rate)

    # ------------------------------------------------------------------
    # Per-tenant aggregate  (Requirement 7.6)
    # ------------------------------------------------------------------

    async def check_tenant_limit(
        self,
        tenant_id: str,
        rate_per_minute: int = DEFAULT_TENANT_RPM,
    ) -> RateLimitResult:
        bucket_key = f"{TENANT_PREFIX}:{tenant_id}:tokens"
        capacity = rate_per_minute
        refill_rate = rate_per_minute / 60.0
        return await self._consume_token(bucket_key, capacity, refill_rate)

    # ------------------------------------------------------------------
    # Global system-wide  (Requirement 7.7)
    # ------------------------------------------------------------------

    async def check_global_limit(
        self,
        rate_per_minute: int = DEFAULT_GLOBAL_RPM,
    ) -> RateLimitResult:
        bucket_key = f"{GLOBAL_KEY}:tokens"
        capacity = rate_per_minute
        refill_rate = rate_per_minute / 60.0
        return await self._consume_token(bucket_key, capacity, refill_rate)

    # ------------------------------------------------------------------
    # Core token bucket logic (shared)
    # ------------------------------------------------------------------

    async def _consume_token(
        self,
        bucket_key: str,
        capacity: float,
        refill_rate: float,
    ) -> RateLimitResult:
        """
        Lazy-refill token bucket stored in two Redis keys:
            ``{bucket_key}``       → current token count
            ``{bucket_key}:last``  → last refill epoch
        """
        now = time.time()
        client = self._redis.get_client()

        try:
            # Read current state
            pipe = client.pipeline()
            pipe.get(bucket_key)
            pipe.get(f"{bucket_key}:last")
            tokens_raw, last_raw = await pipe.execute()

            if tokens_raw is None:
                # First request — initialise at full capacity
                tokens = float(capacity)
                last_refill = now
            else:
                tokens = float(tokens_raw)
                last_refill = float(last_raw) if last_raw else now

            # Lazy refill
            elapsed = now - last_refill
            tokens = min(capacity, tokens + elapsed * refill_rate)

            # Attempt to consume
            if tokens >= 1.0:
                tokens -= 1.0
                allowed = True
            else:
                allowed = False

            # Persist state
            pipe2 = client.pipeline()
            pipe2.set(bucket_key, str(tokens))
            pipe2.set(f"{bucket_key}:last", str(now))
            # Auto-expire keys after 2 minutes of inactivity
            pipe2.expire(bucket_key, 120)
            pipe2.expire(f"{bucket_key}:last", 120)
            await pipe2.execute()

            remaining = max(0, int(tokens))
            reset_at = now + ((capacity - tokens) / refill_rate if refill_rate > 0 else 60)
            retry_after = None if allowed else max(1, int(1.0 / refill_rate)) if refill_rate > 0 else 60

            return RateLimitResult(
                allowed=allowed,
                limit=int(capacity),
                remaining=remaining,
                reset_at=reset_at,
                retry_after=retry_after,
            )

        except Exception as exc:
            logger.error("Rate limit check failed for %s: %s", bucket_key, exc)
            # Fail open — allow the request if Redis is down
            return RateLimitResult(
                allowed=True,
                limit=int(capacity),
                remaining=int(capacity),
                reset_at=now + 60,
            )

    # ------------------------------------------------------------------
    # Admin helpers  (Requirement 7.5)
    # ------------------------------------------------------------------

    async def reset_bucket(self, api_key_id: str) -> bool:
        """Reset rate limit bucket for an API key (admin action)."""
        try:
            client = self._redis.get_client()
            bucket_key = f"{KEY_PREFIX}:{api_key_id}:tokens"
            await client.delete(bucket_key, f"{bucket_key}:last")
            return True
        except Exception as exc:
            logger.error("Failed to reset bucket for %s: %s", api_key_id, exc)
            return False
