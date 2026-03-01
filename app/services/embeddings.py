"""
Embeddings Service.
Converts text prompts into highly dimensional vector payloads (float lists)
so they can be queried using KNN similarity against a vector database.
"""

import httpx
from typing import List, Optional
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

async def get_embedding(text: str, model: str = "text-embedding-3-small") -> Optional[List[float]]:
    """
    Retrieve vector embeddings for a given prompt via OpenAI's lightweight HTTP API.
    Used exclusively for generating vectors for semantic caching comparisons.
    """
    settings = get_settings()
    api_key = settings.providers.openai_api_key
    
    if not api_key and not settings.mock_llm:
        logger.warning("No OPENAI_API_KEY provided; cannot generate embeddings for semantic cache.")
        return None

    if settings.mock_llm:
        # Generate a deterministic but dummy embedding (1536 dims)
        import hashlib
        import struct
        h = hashlib.sha256(text.encode()).digest()
        # Seed it with the hash
        # We need a list of 1536 floats. We'll just repeat some values from the hash.
        # This ensures the same text gets the same dummy embedding.
        seed_floats = [float(b) / 255.0 for b in h] # 32 floats
        return (seed_floats * 48)[:1536] # 32 * 48 = 1536
        
    url = "https://api.openai.com/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "input": text,
        "model": model
    }
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]
    except Exception as e:
        logger.error(f"Failed to generate embedding: {str(e)}")
        return None
