from fastapi import APIRouter, HTTPException, BackgroundTasks
from services.document_ingestion import DocumentIngestionService
from models.rag_models import DocumentType
import os
router = APIRouter()
ingestion_service = DocumentIngestionService()

@router.post("/ingest-documents")
async def ingest_documents(background_tasks: BackgroundTasks):
    """Admin endpoint to trigger document ingestion"""
    background_tasks.add_task(run_ingestion)
    return {"message": "Document ingestion started in background"}

async def run_ingestion():
    """Run the ingestion process"""
    try:
        # Process Financial Aid PDFs
        financial_aid_path = "./data/raw_documents/scholarships/financial_aid_ug.pdf"
        if os.path.exists(financial_aid_path):
            await ingestion_service.process_financial_aid_pdf(financial_aid_path)
        
        # Add other documents as needed
        print("✅ Ingestion completed!")
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")