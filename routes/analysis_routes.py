from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from src.database.models import DocumentRepository
from src.vector_store.manager import VectorStoreManager
from src.rag.summarizer import DocumentSummarizer
from src.rag.comparator import MultiDocumentComparator
from src.ml.predictor import DocumentClassifier

router = APIRouter(prefix="/analysis", tags=["Summarization, Comparison & ML Classification"])

vector_manager = VectorStoreManager()
summarizer = DocumentSummarizer(vector_manager)
comparator = MultiDocumentComparator(vector_manager)
classifier = DocumentClassifier()

class SummarizeRequest(BaseModel):
    doc_id: str

class CompareRequest(BaseModel):
    doc_ids: List[str]

class ClassifyTextRequest(BaseModel):
    text: str

@router.post("/summarize")
async def summarize_document(req: SummarizeRequest):
    """Generates multi-tier structured summary (Executive, Technical, Bullet Points, Key Takeaways)."""
    doc = DocumentRepository.get_document(req.doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    res = summarizer.summarize_document(req.doc_id, doc["file_name"])
    return {
        "doc_id": req.doc_id,
        "file_name": doc["file_name"],
        "summary": res
    }

@router.post("/compare")
async def compare_documents(req: CompareRequest):
    """Compares methodologies, advantages, similarities, and differences across multiple documents."""
    if len(req.doc_ids) < 2:
        raise HTTPException(status_code=400, detail="Comparison requires at least 2 document IDs.")

    doc_targets = []
    for d_id in req.doc_ids:
        doc = DocumentRepository.get_document(d_id)
        if doc:
            doc_targets.append({"doc_id": d_id, "file_name": doc["file_name"]})

    if len(doc_targets) < 2:
        raise HTTPException(status_code=404, detail="Valid document records not found for comparison.")

    res = comparator.compare_documents(doc_targets)
    return res

@router.post("/classify-text")
async def classify_text(req: ClassifyTextRequest):
    """Classifies arbitrary technical text using the TensorFlow / Deep Neural Classifier model."""
    res = classifier.predict(req.text)
    return res
