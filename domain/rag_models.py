from pydantic import BaseModel
from  typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    SCHOLARSHIP = "scholarship"
    ADMISSION = "admission"
    MASTERS = "masters"
    REGISTRATION = "registration"
    FAQ = "faq"
    POLICY = "policy"
    FORM = "form"
    
class DocumentChunk(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    document_type: DocumentType
    source: str
    page_number: Optional[int] = None
    
class RetrievalResult(BaseModel):
    document_chunk: DocumentChunk
    score: float 
    source: str
    
class SearchResult(BaseModel):
    chunk: DocumentChunk
    score: float
    source: str

class RAGResponse(BaseModel):
    answer: str
    sources: List[SearchResult]
    context: str
    confidence: float

