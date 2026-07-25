from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from config.settings import settings
from src.vector_store.manager import VectorStoreManager
from src.database.models import ChatRepository, AnalyticsRepository

class RAGQuestionAnswering:
    """Retrieval-Augmented Generation engine supporting precise citations and conversation memory."""

    def __init__(self, vector_manager: VectorStoreManager):
        self.vector_manager = vector_manager
        self.llm = None
        if settings.OPENAI_API_KEY:
            try:
                self.llm = ChatOpenAI(
                    openai_api_key=settings.OPENAI_API_KEY,
                    model_name=settings.DEFAULT_LLM_MODEL,
                    temperature=0.1
                )
            except Exception as e:
                print(f"Notice initializing ChatOpenAI: {e}")

    def answer_question(
        self,
        query: str,
        session_id: str = "default_session",
        search_mode: str = "hybrid",
        doc_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Executes RAG flow: fetches chunks, incorporates chat history, checks grounding, and formats response.
        """
        # 1. Retrieve top K relevant chunks based on search mode
        if search_mode == "semantic":
            chunks = self.vector_manager.semantic_search(query, top_k=4, doc_ids=doc_ids)
        elif search_mode == "keyword":
            chunks = self.vector_manager.keyword_search(query, top_k=4, doc_ids=doc_ids)
        else:
            chunks = self.vector_manager.hybrid_search(query, top_k=4, doc_ids=doc_ids)

        # 2. Get past session history for conversational memory context
        history_records = ChatRepository.get_session_history(session_id, limit=4)
        formatted_history = ""
        for record in history_records:
            formatted_history += f"User: {record['user_query']}\nAssistant: {record['assistant_response']}\n"

        # 3. Check context coverage
        if not chunks:
            fallback_ans = "I cannot determine the answer from the provided documents because no relevant context was found."
            ChatRepository.add_message(session_id, query, fallback_ans, [])
            AnalyticsRepository.log_query(query, search_mode, doc_ids or [])
            return {
                "answer": fallback_ans,
                "citations": [],
                "retrieved_context": [],
                "confidence_score": 0.0,
                "session_id": session_id
            }

        # 4. Construct context string and citation list
        context_str = ""
        citations = []
        referenced_doc_ids = set()

        for chunk in chunks:
            doc_name = chunk.get("file_name", "Unknown")
            page_no = chunk.get("page_number", 1)
            doc_id = chunk.get("doc_id", "")
            if doc_id:
                referenced_doc_ids.add(doc_id)

            context_str += f"\n--- Source Document: {doc_name} (Page {page_no}) ---\n{chunk['text']}\n"
            citations.append({
                "document": doc_name,
                "page": page_no,
                "doc_id": doc_id
            })

        # 5. Generate LLM answer or heuristic grounded fallback response
        if self.llm:
            prompt_template = """
You are an expert AI Research Assistant. Answer the user's question using ONLY the provided document context below.
If the context does not contain sufficient information to answer the question, state clearly: "I cannot determine the answer from the provided documents."

Conversation History (for resolving references like 'its', 'the paper', 'this'):
{history}

Retrieved Document Context:
{context}

User Question: {question}

Provide a comprehensive, accurate, and direct response strictly grounded in the context above.
"""
            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["history", "context", "question"]
            )
            formatted_prompt = prompt.format(
                history=formatted_history if formatted_history else "None",
                context=context_str,
                question=query
            )

            try:
                res = self.llm.invoke(formatted_prompt)
                answer_text = res.content
            except Exception as e:
                answer_text = self._heuristic_fallback_answer(query, chunks)
        else:
            answer_text = self._heuristic_fallback_answer(query, chunks)

        # 6. Save chat message and analytics
        ChatRepository.add_message(session_id, query, answer_text, citations)
        AnalyticsRepository.log_query(query, search_mode, list(referenced_doc_ids))

        return {
            "answer": answer_text,
            "citations": citations,
            "retrieved_context": [c["text"] for c in chunks],
            "confidence_score": round(max([c.get("score", 0.8) for c in chunks]), 2),
            "session_id": session_id
        }

    def _heuristic_fallback_answer(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        """Grounded answer fallback when external LLM API key is not configured."""
        summary_lines = []
        for c in chunks:
            summary_lines.append(f"• According to **{c['file_name']}** (Page {c['page_number']}): {c['text'][:350]}...")
        
        return f"Based on the retrieved document context:\n\n" + "\n\n".join(summary_lines)
