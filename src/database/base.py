import sqlite3
import os
from config.settings import settings

def get_db_connection():
    """Establishes and returns a SQLite database connection with Row factory."""
    conn = sqlite3.connect(settings.DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes SQLite tables for Metadata, Sessions, and Analytics logging."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Documents Metadata Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            doc_id TEXT PRIMARY KEY,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            total_pages INTEGER DEFAULT 0,
            total_chunks INTEGER DEFAULT 0,
            processing_status TEXT DEFAULT 'PENDING',
            category TEXT DEFAULT 'Unclassified',
            category_confidence REAL DEFAULT 0.0
        )
    """)
    
    # 2. Chat Session History Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            user_query TEXT NOT NULL,
            assistant_response TEXT NOT NULL,
            citations_json TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Query Analytics Tracking Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            search_type TEXT DEFAULT 'semantic',
            doc_ids_referenced TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

# Auto-initialize database on import
init_db()
