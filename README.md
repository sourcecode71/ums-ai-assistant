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

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/ums-ai-assistant.git
cd ums-ai-assistant
