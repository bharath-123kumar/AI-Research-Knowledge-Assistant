from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from src.vector_store.manager import VectorStoreManager
from src.rag.qa_chain import RAGQuestionAnswering

router = APIRouter(prefix="/search", tags=["Semantic Search & RAG"])

vector_manager = VectorStoreManager()
rag_engine = RAGQuestionAnswering(vector_manager)

class QARequest(BaseModel):
    query: str
    session_id: Optional[str] = "default_session"
    search_mode: Optional[str] = "hybrid"  # semantic, keyword, hybrid
    doc_ids: Optional[List[str]] = None

@router.get("/retrieval")
async def retrieve_chunks(
    query: str = Query(..., description="User search query"),
    mode: str = Query("hybrid", description="Search mode: semantic, keyword, or hybrid"),
    top_k: int = Query(4, ge=1, le=20)
):
    """Executes raw vector/keyword retrieval across indexed documents."""
    if mode == "semantic":
        results = vector_manager.semantic_search(query, top_k=top_k)
    elif mode == "keyword":
        results = vector_manager.keyword_search(query, top_k=top_k)
    else:
        results = vector_manager.hybrid_search(query, top_k=top_k)

    return {
        "query": query,
        "mode": mode,
        "total_results": len(results),
        "results": results
    }

@router.post("/qa")
async def answer_question(req: QARequest):
    """RAG Question Answering with citations and conversational memory."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    res = rag_engine.answer_question(
        query=req.query,
        session_id=req.session_id or "default_session",
        search_mode=req.search_mode or "hybrid",
        doc_ids=req.doc_ids
    )
    return res
