import chromadb
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
            # Create persistent client
            self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)

            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="university_documents",
                metadata={"description": "University scholarship and policy documents"}
            )
            print(f"Connected to ChromaDB collection: {self.collection.name}")
        else:
            raise ValueError(f"Unsupported vector DB type: {settings.VECTOR_DB_TYPE}")
        # Add Pinecone/Weaviate support here
    
    async def add_documents(self, chunks: List[DocumentChunk]):
        """
        Add document chunks to vector database

        Args:
            chunks: List of DocumentChunk objects
        """
        if not chunks:
            print("No chunks to add")
            return

        print(f"Adding {len(chunks)} chunks to vector database...")

        # Prepare data for ChromaDB
        ids = []
        documents = []
        metadatas = []

        for chunk in chunks:
            ids.append(chunk.id)
            documents.append(chunk.content)
            metadatas.append(chunk.metadata)

        # Get embeddings for all chunks
        embeddings = await self.embedding_service.get_embeddings(documents)

        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )

        print(f"Successfully added {len(chunks)} chunks")
    
    async def search(self, query: str, document_type: DocumentType = None,
                    limit: int = 5) -> List[SearchResult]:
        """Search for relevant document chunks"""
        query_embedding = await self.embedding_service.get_embeddings([query])

        # Build filter if document_type is specified
        where_filter = {}
        if document_type:
            where_filter = {"document_type": document_type.value}

        try:
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=limit,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )

            search_results = []
            for i in range(len(results['ids'][0])):
                chunk = DocumentChunk(
                    id=results['ids'][0][i],
                    content=results['documents'][0][i],
                    metadata=results['metadatas'][0][i],
                    document_type=DocumentType(results['metadatas'][0][i].get('document_type', 'scholarship')),
                    source=results['metadatas'][0][i].get('source', 'unknown')
                )
                score = 1 - results['distances'][0][i]  # Convert distance to similarity score
                search_results.append(SearchResult(chunk=chunk, score=score, source=chunk.source))

            return search_results

        except Exception as e:
            print(f"Error searching vector database: {e}")
            return []