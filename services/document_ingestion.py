import os
import hashlib
from typing import List
import warnings

from models.rag_models import DocumentChunk, DocumentType
from services.vector_store_service import VectorStoreService
from services.embedding_service import EmbeddingService  # Local embeddings!

try:
    import fitz
except ImportError:
    fitz = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import docx
except ImportError:
    docx = None

class DocumentIngestionService:
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.embedding_service = EmbeddingService()  # Local embeddings
        print("✅ Document Ingestion Service initialized with local embeddings")

    async def ingest_scholarship_document(self, file_path: str, source_name: str):
        """
        Ingest a scholarship document into vector database
        
        Args:
            file_path: Path to PDF/Word/TXT file
            source_name: Name of the document (e.g., "financial_aid_2024")
            
        Returns:
            Number of chunks stored
        """
        print(f"\n📥 Ingesting document: {source_name} from {file_path}")
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return 0
        
        try:
            # 1. Extract text from file
            text_chunks = self._extract_text_from_file(file_path)
            if not text_chunks:
                print(f"⚠️ No text extracted from {source_name}")
                return 0
            print(f"   📄 Extracted {len(text_chunks)} text chunks")
            
            # 2. Create document chunks
            document_chunks = self._create_document_chunks(
                text_chunks, 
                document_type=DocumentType.SCHOLARSHIP,
                source=source_name,
                file_path=file_path
            )
            print(f"   🔧 Created {len(document_chunks)} document chunks")
            
            # 3. Store in vector database
            await self.vector_store.add_documents(document_chunks)
            print(f"✅ Successfully stored {len(document_chunks)} chunks from {source_name}")
            
            return len(document_chunks)
            
        except Exception as e:
            print(f"❌ Error ingesting {source_name}: {str(e)}")
            return 0

    def _extract_text_from_file(self, file_path: str) -> List[str]:
        """Extract text from various file formats"""
        text_chunks = []
        
        try:
            if file_path.lower().endswith('.pdf'):
                # Use pymupdf for better PDF extraction
                if fitz is not None:
                    return self._extract_text_with_pymupdf(file_path)
                else:
                    print("   ⚠️ pymupdf not available, falling back to PyPDF2")
                    return self._extract_text_with_pypdf2(file_path)
                    
            elif file_path.lower().endswith('.txt'):
                return self._extract_text_from_txt(file_path)
                
            elif file_path.lower().endswith('.docx'):
                return self._extract_text_from_docx(file_path)
                
            else:
                print(f"   ⚠️ Unsupported file format: {file_path}")
                return []
                
        except Exception as e:
            print(f"   ❌ Error extracting text from {file_path}: {str(e)}")
            return []

    def _extract_text_with_pymupdf(self, file_path: str) -> List[str]:
        """Extract text using pymupdf (more robust)"""
        text_chunks = []
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                if text and text.strip():
                    chunks = self._split_text_into_chunks(text)
                    text_chunks.extend(chunks)
            doc.close()
            print(f"   📖 Read {len(doc)} pages with pymupdf")
        except Exception as e:
            print(f"   ⚠️ pymupdf error: {e}")
            text_chunks = self._extract_text_with_pypdf2(file_path)
        return text_chunks

    def _extract_text_with_pypdf2(self, file_path: str) -> List[str]:
        """Extract text using PyPDF2 (fallback)"""
        text_chunks = []
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        text = page.extract_text()
                        if text and text.strip():
                            chunks = self._split_text_into_chunks(text)
                            text_chunks.extend(chunks)
                    except Exception as e:
                        print(f"   ⚠️ Error reading page {page_num}: {e}")
                print(f"   📖 Read {len(pdf_reader.pages)} pages with PyPDF2")
        except Exception as e:
            print(f"   ❌ PyPDF2 error: {e}")
        return text_chunks

    def _extract_text_from_txt(self, file_path: str) -> List[str]:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                if text.strip():
                    chunks = self._split_text_into_chunks(text)
                    return chunks
        except Exception as e:
            print(f"   ❌ Error reading TXT file: {e}")
        return []

    def _extract_text_from_docx(self, file_path: str) -> List[str]:
        """Extract text from DOCX file"""
        if docx is None:
            print("   ⚠️ python-docx not installed. Install with: pip install python-docx")
            return []
        try:
            doc = docx.Document(file_path)
            full_text = []
            for para in doc.paragraphs:
                if para.text.strip():
                    full_text.append(para.text)
            text = '\n'.join(full_text)
            if text.strip():
                chunks = self._split_text_into_chunks(text)
                return chunks
        except Exception as e:
            print(f"   ❌ Error reading DOCX file: {e}")
        return []

    def _split_text_into_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """
        Split text into manageable chunks with overlap
        
        Args:
            text: Text to split
            chunk_size: Maximum words per chunk
            overlap: Words to overlap between chunks for context
        """
        if not text or not text.strip():
            return []
            
        words = text.split()
        if len(words) <= chunk_size:
            return [' '.join(words)]
        
        chunks = []
        start = 0
        
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk = ' '.join(words[start:end])
            chunks.append(chunk)
            start = start + chunk_size - overlap  # Overlap for context
            
        print(f"   ✂️  Split text into {len(chunks)} chunks (size: {chunk_size}, overlap: {overlap})")
        return chunks

    def _create_document_chunks(self, text_chunks: List[str],
                              document_type: DocumentType,
                              source: str,
                              file_path: str) -> List[DocumentChunk]:
        """Convert text chunks to DocumentChunk objects"""
        if not text_chunks:
            return []
            
        document_chunks = []
        file_size = os.path.getsize(file_path)
        file_ext = os.path.splitext(file_path)[1].lower()
        
        print(f"   📊 File info: {file_ext.upper()} file, {file_size:,} bytes")
        
        for i, chunk_text in enumerate(text_chunks):
            if not chunk_text or not chunk_text.strip():
                continue
                
            # Create unique ID for each chunk
            content_hash = hashlib.md5(chunk_text.encode()).hexdigest()[:8]
            chunk_id = f"{source}_{i}_{content_hash}"
            
            document_chunk = DocumentChunk(
                id=chunk_id,
                content=chunk_text,
                metadata={
                    "source": source,
                    "file_name": os.path.basename(file_path),
                    "file_path": file_path,
                    "file_size": file_size,
                    "file_type": file_ext,
                    "chunk_index": i,
                    "total_chunks": len(text_chunks),
                    "chunk_hash": content_hash,
                    "document_type": document_type.value,
                    "word_count": len(chunk_text.split())
                },
                document_type=document_type,
                source=source
            )
            document_chunks.append(document_chunk)
        
        return document_chunks

    async def ingest_directory(self, directory_path: str, document_type: DocumentType):
        """
        Ingest all documents in a directory
        
        Args:
            directory_path: Path to directory containing documents
            document_type: Type of documents (e.g., DocumentType.SCHOLARSHIP)
        """
        if not os.path.exists(directory_path):
            print(f"❌ Directory not found: {directory_path}")
            return 0
        
        print(f"\n📁 Processing directory: {directory_path}")
        print(f"📚 Document type: {document_type.value}")
        
        supported_extensions = ['.pdf', '.txt', '.docx']
        total_chunks = 0
        
        files = [f for f in os.listdir(directory_path) 
                if os.path.isfile(os.path.join(directory_path, f))]
        
        print(f"📄 Found {len(files)} files in directory")
        
        for filename in files:
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in supported_extensions:
                file_path = os.path.join(directory_path, filename)
                source_name = os.path.splitext(filename)[0]
                
                chunks = await self.ingest_scholarship_document(file_path, source_name)
                total_chunks += chunks
        
        print(f"\n🎉 Directory ingestion complete!")
        print(f"📊 Total chunks stored: {total_chunks}")
        return total_chunks