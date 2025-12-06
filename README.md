# 🎓 UMS AI Assistant

The **UMS AI Assistant** is an AI-powered document retrieval and question-answering system built using **FastAPI**, **RAG (Retrieval-Augmented Generation)**, and a **Vector Database**.  
It helps university staff query and summarize **financial and administrative documents** securely and efficiently.

---

## 🚀 Project Overview

Universities often have thousands of complex financial documents (e.g., audit reports, student billing summaries, purchase orders).  
This project allows you to upload these PDF documents, convert them into searchable vector embeddings, and use an AI model to answer natural language questions based on document content.

### 🧠 How it works
1. **Upload PDFs** — Admin users can upload one or multiple PDF documents.  
2. **Ingestion Pipeline** — Extracts text, splits into chunks, embeds them, and stores them in a VectorDB.  
3. **Query** — Users ask questions in natural language.  
4. **RAG Pipeline** — The system retrieves the most relevant text chunks and sends them to an LLM (e.g., GPT-4 or local LLM).  
5. **Response** — The model generates an accurate answer with source references.

---

## 🏗️ System Architecture

               ┌─────────────────────────────┐
               │        User (Frontend)      │
               └──────────────┬──────────────┘
                              │   REST API
                              ▼
                  ┌────────────────────────┐
                  │      FastAPI (RAG)     │
                  │   /ingest   /query     │
                  └────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
      ┌───────────────────┐       ┌────────────────────┐
      │  Embedding Model  │       │   Vector Database   │
      │ (OpenAI or local) │──────▶│ (Weaviate/Chroma)  │
      └───────────────────┘       └────────────────────┘
                              │
                              ▼
                       ┌──────────────┐
                       │     LLM API  │
                       │ (GPT-4 / etc)│
                       └──────────────┘

---

## ⚙️ Features

- 📄 PDF ingestion and text extraction  
- 🧩 Automatic text chunking with overlap  
- 🧠 Embedding-based semantic search  
- 🗄️ Vector database integration (Weaviate / Chroma / Pinecone)  
- 💬 FastAPI endpoints for ingestion & querying  
- 🔐 Supports secure, private deployment  
- 🪶 Lightweight, modular architecture for easy customization  

---

## 🧰 Tech Stack

| Component | Technology |
|------------|-------------|
| Backend Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| AI Framework | [LangChain](https://www.langchain.com/) |
| Vector Database | Weaviate / Chroma / Pinecone |
| Embeddings | OpenAI / Sentence-Transformers |
| PDF Parser | pdfplumber / PyMuPDF |
| LLM | GPT-4 / LLaMA / Local models |
| Deployment | Docker / Uvicorn / Nginx |

---

## 🧩 Folder Structure


---

## 🧠 Environment Setup

### Option 1: Using Docker (Recommended)
If you prefer to use Docker, clone the repository and skip to the Docker running instructions below.

### Option 2: Local Setup

#### 1. Clone the repository
```bash
git clone https://github.com/yourusername/ums-ai-assistant.git
cd ums-ai-assistant
```

#### 2. Install dependencies
```bash
pip install -r requirements.txt
```

#### 3. Set up environment variables
Copy the `.env` file and configure your API keys and settings.

---

## 🚀 Running the Application

### Using Docker (Recommended)
To run the application using Docker Compose:
```bash
docker-compose up --build
```

Or build and run with Docker directly:
```bash
docker build -t ums-ai-assistant .
docker run -p 8000:8000 ums-ai-assistant
```

### Local Development
To run the application in development mode with auto-reload:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Local Production
For production deployment with multiple workers:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 🔍 Access Swagger UI
Once the application is running, you can access the API documentation:

- **Interactive Swagger UI (Recommended)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Swagger UI**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI JSON Specification**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)
