#!/usr/bin/env python3
"""
Script to ingest documents into ChromaDB
Run this once to populate your vector database
"""

import asyncio
import os
from services.document_ingestion import DocumentIngestionService
from models.rag_models import DocumentType

async def main():
    ingestion_service = DocumentIngestionService()
    
    # Define your document directories
    document_dirs = {
        DocumentType.SCHOLARSHIP: "./data/raw_documents/scholarship/",
        DocumentType.ADMISSION: "./data/raw_documents/admission/",
        DocumentType.MASTERS: "./data/raw_documents/masters/",
        DocumentType.REGISTRATION: "./data/raw_documents/registration/"
    }
    
    print("Starting document ingestion...")

    # Process each directory
    for doc_type, directory in document_dirs.items():
        if os.path.exists(directory):
            print(f"Processing {doc_type.value} documents from {directory}")
            try:
                await ingestion_service.process_document_directory(directory, doc_type)
            except Exception as e:
                print(f"Error processing directory {directory}: {str(e)}")
        else:
            print(f"Directory not found: {directory}")

    print("Document ingestion completed!")

if __name__ == "__main__":
    asyncio.run(main())