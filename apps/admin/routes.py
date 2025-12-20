from fastapi import APIRouter, HTTPException, BackgroundTasks
from services.document_ingestion import DocumentIngestionService
from models.rag_models import DocumentType
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
    
    This function handles finding specific documents (like financial aid PDFs)
    and passing them to the ingestion service.
    """
    try:
        # Process Financial Aid PDFs
        financial_aid_path = "./data/raw_documents/scholarships/financial_aid_ug.pdf"
        if os.path.exists(financial_aid_path):
            await ingestion_service.ingest_scholarship_document(financial_aid_path, "financial_aid_ug")

        # Placeholder: Add other documents as needed
        
        print("✅ Ingestion completed!")
    except Exception as e:
        # Log any exceptions that occur during ingestion
        print(f"❌ Ingestion failed: {e}")