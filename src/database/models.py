import json
from typing import List, Dict, Any, Optional
from src.database.base import get_db_connection

class DocumentRepository:
    @staticmethod
    def create_document(doc_id: str, file_name: str, file_path: str, category: str = "Unclassified") -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO documents (doc_id, file_name, file_path, processing_status, category)
            VALUES (?, ?, ?, 'PENDING', ?)
            """,
            (doc_id, file_name, file_path, category)
        )
        conn.commit()
        conn.close()
        return DocumentRepository.get_document(doc_id)

    @staticmethod
    def update_status(doc_id: str, status: str, total_pages: int = 0, total_chunks: int = 0, category: str = None, confidence: float = 0.0):
        conn = get_db_connection()
        cursor = conn.cursor()
        if category:
            cursor.execute(
                """
                UPDATE documents 
                SET processing_status = ?, total_pages = ?, total_chunks = ?, category = ?, category_confidence = ?
                WHERE doc_id = ?
                """,
                (status, total_pages, total_chunks, category, confidence, doc_id)
            )
        else:
            cursor.execute(
                """
                UPDATE documents 
                SET processing_status = ?, total_pages = ?, total_chunks = ?
                WHERE doc_id = ?
                """,
                (status, total_pages, total_chunks, doc_id)
            )
        conn.commit()
        conn.close()

    @staticmethod
    def get_document(doc_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE doc_id = ?", (doc_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def list_documents() -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents ORDER BY upload_timestamp DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def delete_document(doc_id: str) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM documents WHERE doc_id = ?", (doc_id,))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0


class ChatRepository:
    @staticmethod
    def add_message(session_id: str, user_query: str, assistant_response: str, citations: list):
        conn = get_db_connection()
        cursor = conn.cursor()
        citations_str = json.dumps(citations)
        cursor.execute(
            """
            INSERT INTO chat_sessions (session_id, user_query, assistant_response, citations_json)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, user_query, assistant_response, citations_str)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_session_history(session_id: str, limit: int = 6) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT user_query, assistant_response FROM chat_sessions
            WHERE session_id = ?
            ORDER BY id ASC
            LIMIT ?
            """,
            (session_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


class AnalyticsRepository:
    @staticmethod
    def log_query(query: str, search_type: str, doc_ids: List[str]):
        conn = get_db_connection()
        cursor = conn.cursor()
        doc_ids_str = ",".join(doc_ids) if doc_ids else ""
        cursor.execute(
            """
            INSERT INTO query_analytics (query, search_type, doc_ids_referenced)
            VALUES (?, ?, ?)
            """,
            (query, search_type, doc_ids_str)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as total_docs FROM documents")
        total_docs = cursor.fetchone()["total_docs"]
        
        cursor.execute("SELECT SUM(total_chunks) as total_chunks FROM documents")
        res_chunks = cursor.fetchone()["total_chunks"]
        total_chunks = res_chunks if res_chunks else 0
        
        cursor.execute("SELECT COUNT(*) as total_queries FROM query_analytics")
        total_queries = cursor.fetchone()["total_queries"]
        
        cursor.execute("SELECT category, COUNT(*) as count FROM documents GROUP BY category")
        category_dist = {row["category"]: row["count"] for row in cursor.fetchall()}
        
        cursor.execute("SELECT query, search_type, timestamp FROM query_analytics ORDER BY id DESC LIMIT 10")
        recent_queries = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return {
            "total_documents": total_docs,
            "total_processed_chunks": total_chunks,
            "total_questions_answered": total_queries,
            "category_distribution": category_dist,
            "recent_queries": recent_queries
        }
