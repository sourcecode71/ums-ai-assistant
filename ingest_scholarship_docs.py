#!/usr/bin/env python3
"""
Script to ingest scholarship documents into vector database
"""

import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.document_ingestion import DocumentIngestionService
from models.rag_models import DocumentType

async def main():
    """Main ingestion function"""
    print("Starting document ingestion...")

    ingestion_service = DocumentIngestionService()

    # Path to your scholarship documents
    scholarship_dir = "./data/raw_documents/scholarships/"

    if not os.path.exists(scholarship_dir):
        print(f"Directory not found: {scholarship_dir}")
        print("Creating directory structure...")
        os.makedirs(scholarship_dir, exist_ok=True)
        print(f"Created {scholarship_dir}")
        print("Please add your scholarship PDFs to this directory and run again.")
        return

    # Get all PDF files
    pdf_files = [f for f in os.listdir(scholarship_dir) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print(f"No PDF files found in {scholarship_dir}")
        print("Add your scholarship PDFs (e.g., financial_aid.pdf) to this directory")
        return

    print(f"Found {len(pdf_files)} PDF files:")
    for pdf in pdf_files:
        print(f"   - {pdf}")

    # Ingest each PDF
    total_chunks = 0
    for pdf_file in pdf_files:
        file_path = os.path.join(scholarship_dir, pdf_file)
        source_name = os.path.splitext(pdf_file)[0]  # Remove .pdf extension

        try:
            chunks_count = await ingestion_service.ingest_document(
                file_path=file_path,
                source_name=source_name,
                document_type=DocumentType.SCHOLARSHIP
            )
            total_chunks += chunks_count
        except Exception as e:
            print(f"Error ingesting {pdf_file}: {e}")

    print(f"\nIngestion complete! Total chunks stored: {total_chunks}")
    print("You can now query the vector database through your FastAPI endpoints!")

if __name__ == "__main__":
    asyncio.run(main())