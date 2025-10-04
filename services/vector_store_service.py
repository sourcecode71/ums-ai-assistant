from typing import List, Optional
from models.rag_models import DocumentChunk, SearchResult, DocumentType
from services.embedding_service import EmbeddingService
from core.config import settings

class VectorStoreService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.setup_vector_db()
    
    def setup_vector_db(self):
        if settings.VECTOR_DB_TYPE == "chroma":
            try:
                from chromadb import PersistentClient
            except ImportError:
                raise ImportError("ChromaDB library not installed. Install with: pip install chromadb")
            self.client = PersistentClient(path=settings.CHROMA_DB_PATH)
            self.collection = self.client.get_or_create_collection("university_documents")
        else:
            raise ValueError(f"Unsupported vector DB type: {settings.VECTOR_DB_TYPE}")
        # Add Pinecone/Weaviate support here
    
    async def add_documents(self, chunks: List[DocumentChunk]):
        embeddings = await self.embedding_service.get_embeddings(
            [chunk.content for chunk in chunks]
        )
        
        ids = [chunk.id for chunk in chunks]
        documents = [chunk.content for chunk in chunks]
        metadatas = [{
            **chunk.metadata,
            "document_type": chunk.document_type.value,
            "source": chunk.source
        } for chunk in chunks]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
    
    async def search(self, query: str, document_type: Optional[DocumentType] = None, 
                    limit: int = 5) -> List[SearchResult]:
        query_embedding = await self.embedding_service.get_embeddings([query])
        
        where = {}
        if document_type:
            where["document_type"] = document_type.value
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=limit,
            where=where
        )
        
        search_results = []
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0], 
            results['metadatas'][0], 
            results['distances'][0]
        )):
            chunk = DocumentChunk(
                id=results['ids'][0][i],
                content=doc,
                metadata=metadata,
                document_type=DocumentType(metadata.get('document_type')),
                source=metadata.get('source')
            )
            search_results.append(SearchResult(chunk=chunk, score=1-distance, source=metadata.get('source')))
        
        return search_results