from fastapi import APIRouter, HTTPException, BackgroundTasks
from infrastructure.document_ingestion import DocumentIngestionService
from domain import DocumentType
import os

# Initialize the API router for admin routes
router = APIRouter()

# Initialize the document ingestion service instance
ingestion_service = DocumentIngestionService()

@router.post("/ingest-documents")
async def ingest_documents(background_tasks: BackgroundTasks):
    """Admin endpoint to trigger document ingestion"""
    background_tasks.add_task(run_ingestion)
    return {"message": "Document ingestion started in background"}

async def run_ingestion():
    """
    Background task to execute the document ingestion process.

    This function ingests all documents in the scholarships and admission directories.
    """
    try:
        # Ingest all documents in the scholarships directory
        scholarships_dir = "./data/raw_documents/scholarships"
        await ingestion_service.ingest_directory(scholarships_dir, DocumentType.SCHOLARSHIP)

        # Ingest all documents in the admission directory
        admission_dir = "./data/raw_documents/admission"
        await ingestion_service.ingest_directory(admission_dir, DocumentType.ADMISSION)

        print("✅ Ingestion completed!")
    except Exception as e:
        # Log any exceptions that occur during ingestion
        print(f"❌ Ingestion failed: {e}")