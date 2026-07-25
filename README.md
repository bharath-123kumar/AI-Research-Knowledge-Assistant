# # Enterprise AI Research & Knowledge Assistant

An enterprise-grade, production-oriented **AI Research & Knowledge Assistant** designed to ingest, process, analyze, and query multi-page PDF documents. The system integrates **Retrieval-Augmented Generation (RAG)** with precise page-level citations, **Hybrid Search**, **TensorFlow / Neural Document Classification**, **Multi-document Summarization & Comparison**, and **Session Conversation Memory**.

---

## 🌟 Key Features

1. **Document Management & Ingestion**:
   - Upload, track metadata, reprocess, and delete multi-page PDFs.
   - Preserves exact page-level numbers and chunk metadata.
2. **Automated ML Document Classification**:
   - Trains and deploys a Deep Neural Network classifier to categorize documents into domains (*Artificial Intelligence*, *Machine Learning*, *Computer Vision*, *Natural Language Processing*, *Robotics*, *Cyber Security*, *Cloud Computing*).
3. **Hybrid & Semantic Retrieval**:
   - **Semantic Search**: Dense vector embeddings via `SentenceTransformer(all-MiniLM-L6-v2)` stored in persistent **ChromaDB**.
   - **Keyword Search**: Exact token matching.
   - **Hybrid Search**: Combines dense vector similarity and sparse keyword scores for high recall & precision.
4. **RAG Question Answering with Citations & Memory**:
   - Generates answers strictly grounded in retrieved document context.
   - Returns explicit page and file citations (`Source Document: paper.pdf (Page 2)`).
   - Session-based conversation memory handles follow-up references (*"What are its limitations?"*).
5. **Summarization & Multi-Doc Comparison**:
   - Multi-tier structured summarization: **Executive Summary**, **Technical Summary**, **Bullet Points**, **Key Takeaways**.
   - Multi-document comparison matrix analyzing **Methodologies**, **Pros/Cons**, **Similarities**, and **Differences**.
6. **System Analytics Dashboard**:
   - Real-time tracking of total indexed documents, text chunks, questions answered, and category distribution.
7. **Interactive Web Dashboard + OpenAPI / Swagger Documentation**:
   - Built-in web user interface at `http://localhost:8000`.
   - OpenAPI documentation accessible at `http://localhost:8000/docs`.

---

## 🏗️ Architecture Overview

```
                      ┌──────────────────────┐
                      │   PDF Upload (UI/API)│
                      └──────────┬───────────┘
                                 │
                                 ▼
                 ┌────────────────────────────────┐
                 │  PyMuPDF Parser & Metadata     │
                 └───────────────┬────────────────┘
                                 │
                 ┌───────────────┴────────────────┐
                 ▼                                ▼
     ┌────────────────────────┐       ┌──────────────────────┐
     │  Recursive Chunker     │       │ TensorFlow / ML      │
     │  (~1000 len, 150 ov)   │       │ Domain Classifier    │
     └───────────┬────────────┘       └──────────────────────┘
                 │
                 ▼
     ┌────────────────────────┐       ┌──────────────────────┐
     │ ChromaDB Vector Index  │ ◄───► │ Sentence Transformers│
     └───────────┬────────────┘       │ (all-MiniLM-L6-v2)   │
                 │                    └──────────────────────┘
                 ▼
┌────────────────────────────────────────────────────────────┐
│              RAG QA Engine + Session Memory                │
│    (Combines Hybrid Retrieval, History & Page Citations)   │
└──────────────────────────────┬─────────────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Grounded UI Response│
                    └─────────────────────┘
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.10/3.11/3.14)
- Pip

### 2. Environment Setup & Installation
Clone the repository and install project dependencies:

```bash
# Clone repository
git clone https://github.com/your-username/ai-research-assistant.git
cd ai-research-assistant

# Install dependencies
pip install -r requirements.txt
```

### 3. Launch Application Server
Run the FastAPI app via Uvicorn:

```bash
python main.py
# OR
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser and navigate to:
- **Interactive Web Interface**: `http://localhost:8000`
- **Swagger API Docs**: `http://localhost:8000/docs`

---

## 🧪 Testing

Run automated pytest unit test suite:

```bash
python -m pytest tests/test_assistant.py
```

---

## 📂 Project Directory Structure

```
ai-research-assistant/
│
├── config/
│   ├── __init__.py
│   └── settings.py              # Application settings & environment configuration
│
├── data/
│   ├── raw_documents/           # Stored uploaded PDF files
│   ├── vector_db/               # Persistent ChromaDB vector index
│   └── dataset/                 # Dataset for ML classification
│
├── models/
│   ├── tf_classifier.h5         # Saved Trained Neural Network Classifier
│   └── tokenizer.pickle         # Saved TF-IDF Feature Extractor
│
├── src/
│   ├── database/
│   │   ├── base.py              # SQLite session & connection manager
│   │   └── models.py            # Metadata, Chat Session & Analytics repositories
│   │
│   ├── document_processing/
│   │   ├── pdf_parser.py        # PyMuPDF text & page extractor
│   │   └── chunker.py           # Recursive chunker with context overlap
│   │
│   ├── ml/
│   │   ├── dataset_prep.py      # Category dataset builder
│   │   ├── train_classifier.py  # Model training pipeline
│   │   └── predictor.py         # ML domain prediction engine
│   │
│   ├── vector_store/
│   │   └── manager.py           # ChromaDB dense, sparse & hybrid retrieval
│   │
│   ├── rag/
│   │   ├── qa_chain.py          # RAG QA chain with page citations & session memory
│   │   ├── summarizer.py        # Executive/Technical/Key Takeaways summarization
│   │   └── comparator.py        # Multi-document comparative engine
│   │
│   └── analytics/
│       └── metrics.py           # Dashboard system analytics engine
│
├── routes/
│   ├── document_routes.py       # Endpoints: upload, list, delete, reprocess
│   ├── search_routes.py         # Endpoints: retrieval, RAG QA
│   ├── analysis_routes.py       # Endpoints: summarize, compare, classify
│   └── analytics_routes.py      # Endpoints: dashboard metrics
│
├── static/                      # Web UI Dashboard (HTML, CSS, JS)
├── sample_documents/            # Sample research PDFs for quick testing
├── tests/                       # Pytest unit tests
├── main.py                      # FastAPI application entrypoint
├── requirements.txt             # Dependency requirements
└── README.md                    # Repository documentation
```

---

## 🛠️ REST API Endpoints Overview

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/v1/documents/upload` | Upload PDF & trigger auto-chunking and classification |
| `GET` | `/api/v1/documents` | List all uploaded documents with processing status |
| `DELETE` | `/api/v1/documents/{doc_id}` | Delete PDF document and associated vector embeddings |
| `POST` | `/api/v1/search/qa` | Execute RAG QA with page citations and memory |
| `GET` | `/api/v1/search/retrieval` | Retrieve raw vector/keyword chunks |
| `POST` | `/api/v1/analysis/summarize` | Generate multi-tier structured document summary |
| `POST` | `/api/v1/analysis/compare` | Multi-document comparative analysis |
| `POST` | `/api/v1/analysis/classify-text` | Classify technical text using ML model |
| `GET` | `/api/v1/analytics/dashboard` | Get knowledge base analytics and query logs |

---

## 💡 Assumptions & Design Decisions
1. **Intelligent Overlapping Chunking**: Used 1000 characters chunk size with 150 overlap to preserve boundary context across adjacent segments.
2. **Hybrid Search**: Dense vector cosine similarity provides semantic understanding while BM25/keyword matching guarantees precision for domain terminology.
3. **ML Classifier**: Multi-Layer Perceptron (Neural Network with ReLU hidden layers & Softmax output) trained on TF-IDF n-gram feature matrices to classify uploaded documents automatically into 7 tech domains.
4. **Resilient RAG Pipeline**: Provides grounded citations using retrieved chunks with page numbers. If an OpenAI API key is missing, it falls back to a structured, citations-annotated summary extraction.
