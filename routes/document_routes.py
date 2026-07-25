from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
import os
import uuid
from typing import List
from config.settings import settings
from src.database.models import DocumentRepository
from src.document_processing.pdf_parser import PDFParser
from src.document_processing.chunker import RecursiveChunker
from src.ml.predictor import DocumentClassifier
from src.vector_store.manager import VectorStoreManager

router = APIRouter(prefix="/documents", tags=["Document Management"])

# Dependency instances
pdf_parser = PDFParser()
chunker = RecursiveChunker()
classifier = DocumentClassifier()
vector_manager = VectorStoreManager()

def process_pdf_pipeline(doc_id: str, file_path: str, file_name: str):
    """Background task executing parsing, TF/ML classification, chunking, and vector indexing."""
    try:
        # 1. Parse text and page metadata
        pages_data = pdf_parser.extract_pages(file_path, doc_id, file_name)
        total_pages = len(pages_data)
        
        if not pages_data:
            DocumentRepository.update_status(doc_id, "FAILED", 0, 0, "Unclassified", 0.0)
            return

        # 2. Document Domain Classification
        sample_text = " ".join([p["text"] for p in pages_data[:3]])
        class_res = classifier.predict(sample_text)
        predicted_category = class_res["category"]
        confidence = class_res["confidence"]

        # 3. Create chunks
        chunks = chunker.create_chunks(pages_data)
        total_chunks = len(chunks)

        # 4. Index into Vector Store
        vector_manager.add_chunks(chunks)

        # 5. Update SQLite status
        DocumentRepository.update_status(
            doc_id=doc_id,
            status="PROCESSED",
            total_pages=total_pages,
            total_chunks=total_chunks,
            category=predicted_category,
            confidence=confidence
        )
    except Exception as e:
        print(f"Error processing PDF pipeline for {doc_id}: {e}")
        DocumentRepository.update_status(doc_id, "FAILED")

@router.post("/upload")
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Uploads a PDF document, registers metadata, and triggers background processing."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    doc_id = str(uuid.uuid4())
    file_path = os.path.join(settings.RAW_DOCUMENTS_DIR, f"{doc_id}_{file.filename}")

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Create metadata record
    doc_record = DocumentRepository.create_document(
        doc_id=doc_id,
        file_name=file.filename,
        file_path=file_path
    )

    # Trigger background pipeline
    background_tasks.add_task(process_pdf_pipeline, doc_id, file_path, file.filename)

    return {
        "message": "Document uploaded successfully. Processing pipeline started.",
        "document": doc_record
    }

@router.get("")
async def list_documents():
    """Lists all uploaded documents with metadata and processing status."""
    return {"documents": DocumentRepository.list_documents()}

@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    """Deletes uploaded PDF file, SQLite metadata, and associated vector chunks."""
    doc = DocumentRepository.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Remove physical file
    if os.path.exists(doc["file_path"]):
        try:
            os.remove(doc["file_path"])
        except Exception:
            pass

    # Remove vector DB index
    vector_manager.delete_document_chunks(doc_id)

    # Delete SQLite metadata
    DocumentRepository.delete_document(doc_id)

    return {"message": f"Document {doc_id} and associated vector embeddings deleted successfully."}

@router.post("/{doc_id}/reprocess")
async def reprocess_document(doc_id: str, background_tasks: BackgroundTasks):
    """Triggers complete reprocessing of an uploaded document."""
    doc = DocumentRepository.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    DocumentRepository.update_status(doc_id, "PROCESSING")
    background_tasks.add_task(process_pdf_pipeline, doc_id, doc["file_path"], doc["file_name"])

    return {"message": f"Reprocessing pipeline launched for document {doc_id}."}
