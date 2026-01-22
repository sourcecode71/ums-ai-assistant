import asyncio
from typing import List
import numpy as np
from core.config import settings


class EmbeddingService:
    def __init__(self):
        self.provider = settings.EMBEDDING_PROVIDER  # "local" or "openai"
        self.model_name = settings.EMBEDDING_MODEL

        if self.provider == "local":
            self._load_local_model()
        elif self.provider == "openai":
            self._setup_openai()
        else:
            raise ValueError(f"Unsupported embedding provider: {self.provider}")

    def _load_local_model(self):
        """Load FREE local embedding model"""
        try:
            from sentence_transformers import SentenceTransformer

            print(f"📥 Loading local embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            print("✅ Local embedding model loaded (FREE to use!)")

        except ImportError:
            print("❌ sentence-transformers not installed!")
            print("💡 Install with: pip install sentence-transformers")
            raise

    def _setup_openai(self):
        """Setup OpenAI embeddings (paid)"""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment variables")
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        except ImportError:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings - FREE locally or paid via OpenAI"""
        if not texts:
            return []

        if self.provider == "local":
            # ✅ FREE local embeddings
            return await self._local_embeddings(texts)
        elif self.provider == "openai":
            # ❌ Paid OpenAI embeddings
            return await self._openai_embeddings(texts)

    async def _local_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings locally - NO COST!"""
        try:
            # Convert to embeddings
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=True if len(texts) > 10 else False
            )

            print(f"🔢 Generated {len(embeddings)} local embeddings (FREE)")
            return embeddings.tolist()

        except Exception as e:
            print(f"❌ Local embedding error: {e}")
            raise

    async def _openai_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI (costs money)"""
        # OpenAI embeddings API is synchronous, but we'll wrap it in asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.embeddings.create(
                input=texts,
                model=self.model_name
            )
        )
        return [embedding.embedding for embedding in response.data]