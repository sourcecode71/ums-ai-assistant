import os
from pypdf import PdfReader
from typing import List, Dict, Any
from models.rag_models import DocumentChunk, DocumentType
from services.vector_store_service import VectorStoreService
from services.embedding_service import EmbeddingService

class DocumentIngestionService:
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.embedding_service = EmbeddingService()
    
    async def process_financial_aid_pdf(self, file_path: str):
        """Process a single Financial Aid PDF file"""
        try:
            print(f"Processing Financial Aid PDF: {file_path}")

            # Extract text from PDF
            text_chunks = self._extract_text_from_pdf(file_path)

            if not text_chunks:
                print(f"Warning: No text extracted from {file_path}, skipping.")
                return

            # Create document chunks
            document_chunks = self._create_document_chunks(
                text_chunks,
                document_type=DocumentType.SCHOLARSHIP,
                source=os.path.basename(file_path)
            )

            # Store in vector database
            await self.vector_store.add_documents(document_chunks)
            print(f"Successfully stored {len(document_chunks)} chunks from {file_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            # Continue with other files
    
    async def process_document_directory(self, directory_path: str, document_type: DocumentType):
        """Process all documents in a directory"""
        supported_extensions = ['.pdf', '.docx', '.txt']

        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            file_ext = os.path.splitext(filename)[1].lower()

            if file_ext in supported_extensions:
                try:
                    if file_ext == '.pdf':
                        await self.process_financial_aid_pdf(file_path)
                    else:
                        print(f"Unsupported file type for {file_path}, skipping.")
                    # Add other file type handlers here
                except Exception as e:
                    print(f"Error processing file {file_path}: {str(e)}")
                    continue
    
    def _extract_text_from_pdf(self, file_path: str) -> List[str]:
        """Extract and chunk text from PDF"""
        text_chunks = []

        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)

                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            # Split page text into smaller chunks (optional)
                            chunks = self._split_text_into_chunks(page_text)
                            text_chunks.extend(chunks)
                    except Exception as e:
                        print(f"Warning: Error extracting text from page {page_num} of {file_path}: {str(e)}")
                        continue
        except Exception as e:
            print(f"Error reading PDF {file_path}: {str(e)}")
            return []

        return text_chunks
    
    def _split_text_into_chunks(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into manageable chunks by characters"""
        chunks = []

        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size].strip()
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)

        return chunks
    
    def _create_document_chunks(self, text_chunks: List[str], 
                              document_type: DocumentType, 
                              source: str) -> List[DocumentChunk]:
        """Convert text chunks to DocumentChunk objects"""
        document_chunks = []
        
        for i, chunk_text in enumerate(text_chunks):
            chunk_id = f"{source}_{i}"
            
            document_chunk = DocumentChunk(
                id=chunk_id,
                content=chunk_text,
                metadata={
                    "source": source,
                    "chunk_index": i,
                    "document_type": document_type.value,
                    "total_chunks": len(text_chunks)
                },
                document_type=document_type,
                source=source
            )
            document_chunks.append(document_chunk)
        
        return document_chunks