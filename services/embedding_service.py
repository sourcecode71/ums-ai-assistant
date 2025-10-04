from core.config import settings
from typing import List
import asyncio


class EmbeddingService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER  # Assuming same provider for embeddings
        self.model = settings.EMBEDDING_MODEL
        self.setup_client()
        
    def setup_client(self):
        if self.provider == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set in environment variables")
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except ImportError:
                raise ImportError("OpenAI library not installed. Install with: pip install openai")
        else:
            raise ValueError(f"Unsupported embedding provider: {self.provider}")
        
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        if self.provider == "openai":
            return await self._openai_embeddings(texts)
        else:
            raise ValueError(f"Unsupported embedding provider: {self.provider}")
    
    async def _openai_embeddings(self, texts: List[str]) -> List[List[float]]:
        # OpenAI embeddings API is synchronous, but we'll wrap it in asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.embeddings.create(
                input=texts,
                model=self.model
            )
        )
        return [embedding.embedding for embedding in response.data]