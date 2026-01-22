import chromadb
from typing import List, Optional
from domain import DocumentChunk, SearchResult, DocumentType
from infrastructure.embedding_service import EmbeddingService
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
        """Advanced hybrid search with dense and sparse components using RRF"""
        return await self.advanced_hybrid_search(query, document_type, limit)

    async def advanced_hybrid_search(self, query: str, document_type: DocumentType = None,
                                    limit: int = 10) -> List[SearchResult]:
        """More sophisticated hybrid search with separate components"""

        # Run parallel searches
        dense_results = await self.dense_search(query, document_type, limit * 3)
        sparse_results = await self.sparse_search(query, document_type, limit * 3)

        # Fuse using Reciprocal Rank Fusion (RRF)
        fused_results = self._reciprocal_rank_fusion(
            dense_results, sparse_results, k=60
        )

        return fused_results[:limit]

    async def dense_search(self, query: str, document_type: DocumentType = None,
                          limit: int = 10) -> List[SearchResult]:
        """Semantic search using embeddings"""
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
            print(f"Error in dense search: {e}")
            return []

    async def sparse_search(self, query: str, document_type: DocumentType = None,
                           limit: int = 10) -> List[SearchResult]:
        """Keyword-based search using BM25-style ranking"""

        # Extract key terms from query
        key_terms = self._extract_key_terms(query)

        # Build filter for document type
        where_filter = {}
        if document_type:
            where_filter = {"document_type": document_type.value}

        try:
            # Use Chroma's built-in text search capabilities
            results = self.collection.query(
                query_texts=[query],  # This enables text-based search
                n_results=limit * 2,  # Get more results for better ranking
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

                # Calculate BM25-style score based on term frequency
                bm25_score = self._calculate_bm25_score(chunk.content, key_terms)
                score = min(bm25_score, 1.0)  # Normalize to 0-1

                search_results.append(SearchResult(chunk=chunk, score=score, source=chunk.source))

            # Sort by BM25 score
            search_results.sort(key=lambda x: x.score, reverse=True)
            return search_results[:limit]

        except Exception as e:
            print(f"Error in sparse search: {e}")
            return []

    def _reciprocal_rank_fusion(self, results_a: List[SearchResult],
                               results_b: List[SearchResult], k: int = 60) -> List[SearchResult]:
        """Fuse two ranked lists using Reciprocal Rank Fusion"""
        scores = {}

        # Score first list
        for rank, result in enumerate(results_a):
            scores[result.chunk.id] = scores.get(result.chunk.id, 0) + 1 / (k + rank + 1)

        # Score second list
        for rank, result in enumerate(results_b):
            scores[result.chunk.id] = scores.get(result.chunk.id, 0) + 1 / (k + rank + 1)

        # Get all unique chunks
        all_chunks = {result.chunk.id: result for result in results_a + results_b}

        # Sort by fused score
        sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        return [all_chunks[chunk_id] for chunk_id, _ in sorted_ids]

    def _extract_key_terms(self, query: str) -> List[str]:
        """Extract key terms from query for sparse search"""
        # Simple term extraction - split and filter
        terms = query.lower().split()
        # Remove common stop words and short terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall'}
        key_terms = [term for term in terms if len(term) > 2 and term not in stop_words]
        return key_terms[:5]  # Limit to top 5 terms

    def _calculate_bm25_score(self, text: str, key_terms: List[str]) -> float:
        """Calculate BM25-style score for text given key terms"""
        text_lower = text.lower()
        score = 0.0

        for term in key_terms:
            # Simple term frequency
            tf = text_lower.count(term)
            if tf > 0:
                # BM25-like scoring: tf / (tf + k1) where k1=1.5
                score += tf / (tf + 1.5)

        # Normalize by document length (shorter docs get slight boost)
        doc_length_factor = min(len(text.split()) / 100.0, 1.0)
        score = score * (1 + doc_length_factor)

        return score