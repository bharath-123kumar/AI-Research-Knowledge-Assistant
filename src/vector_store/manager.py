import os
from typing import List, Dict, Any, Optional
import chromadb
from sentence_transformers import SentenceTransformer
from config.settings import settings

class VectorStoreManager:
    """Manages dense vector indexing, semantic search, keyword search, and hybrid retrieval."""
    
    def __init__(self):
        os.makedirs(settings.VECTOR_DB_DIR, exist_ok=True)
        # Initialize persistent Chroma DB client
        self.chroma_client = chromadb.PersistentClient(path=settings.VECTOR_DB_DIR)
        self.collection = self.chroma_client.get_or_create_collection(name="document_chunks")
        
        # Load local sentence-transformer embedding model
        print("Loading SentenceTransformer embedding engine (all-MiniLM-L6-v2)...")
        self.embedder = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """Embeds and indexes document chunks into ChromaDB."""
        if not chunks:
            return

        ids = [c["chunk_id"] for c in chunks]
        texts = [c["text"] for c in chunks]
        metadatas = [
            {
                "doc_id": c["doc_id"],
                "file_name": c["file_name"],
                "page_number": int(c["page_number"])
            }
            for c in chunks
        ]

        # Generate dense embeddings
        embeddings = self.embedder.encode(texts, show_progress_bar=False).tolist()

        # Add or update in vector database
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

    def delete_document_chunks(self, doc_id: str):
        """Deletes all chunks belonging to a specific document."""
        try:
            self.collection.delete(where={"doc_id": doc_id})
        except Exception as e:
            print(f"Notice during chunk deletion for {doc_id}: {e}")

    def semantic_search(self, query: str, top_k: int = 4, doc_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Dense vector cosine similarity search."""
        query_embedding = self.embedder.encode([query]).tolist()[0]
        
        where_filter = None
        if doc_ids and len(doc_ids) == 1:
            where_filter = {"doc_id": doc_ids[0]}
        elif doc_ids and len(doc_ids) > 1:
            where_filter = {"$or": [{"doc_id": d} for d in doc_ids]}

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter
        )

        formatted = []
        if results and results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0] if "distances" in results else [0.0]*len(docs)

            for text, meta, dist in zip(docs, metas, distances):
                formatted.append({
                    "text": text,
                    "file_name": meta.get("file_name", "Unknown"),
                    "page_number": meta.get("page_number", 1),
                    "doc_id": meta.get("doc_id", ""),
                    "score": round(1.0 - float(dist) if dist <= 1.0 else float(dist), 4),
                    "type": "semantic"
                })
        return formatted

    def keyword_search(self, query: str, top_k: int = 4, doc_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Exact token & substring matching across indexed documents."""
        # Query ChromaDB documents and filter by keyword matching score
        all_data = self.collection.get()
        if not all_data or not all_data.get("documents"):
            return []

        docs = all_data["documents"]
        metas = all_data["metadatas"]
        query_terms = [t.lower() for t in query.split() if len(t) > 2]

        matches = []
        for text, meta in zip(docs, metas):
            if doc_ids and meta.get("doc_id") not in doc_ids:
                continue
            
            text_lower = text.lower()
            match_score = sum(text_lower.count(term) for term in query_terms)

            if match_score > 0:
                matches.append({
                    "text": text,
                    "file_name": meta.get("file_name", "Unknown"),
                    "page_number": meta.get("page_number", 1),
                    "doc_id": meta.get("doc_id", ""),
                    "score": float(match_score),
                    "type": "keyword"
                })

        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches[:top_k]

    def hybrid_search(self, query: str, top_k: int = 4, doc_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Hybrid search combining dense vector similarity and sparse keyword matching for optimal recall.
        """
        semantic_results = self.semantic_search(query, top_k=top_k, doc_ids=doc_ids)
        keyword_results = self.keyword_search(query, top_k=top_k, doc_ids=doc_ids)

        seen_texts = set()
        hybrid_combined = []

        # Merge semantic results
        for item in semantic_results:
            if item["text"] not in seen_texts:
                seen_texts.add(item["text"])
                hybrid_combined.append(item)

        # Merge keyword results
        for item in keyword_results:
            if item["text"] not in seen_texts:
                seen_texts.add(item["text"])
                hybrid_combined.append(item)

        return hybrid_combined[:top_k]

    def get_document_all_chunks(self, doc_id: str) -> List[Dict[str, Any]]:
        """Fetches all text chunks belonging to a document for summarization."""
        res = self.collection.get(where={"doc_id": doc_id})
        chunks = []
        if res and res.get("documents"):
            for text, meta in zip(res["documents"], res["metadatas"]):
                chunks.append({
                    "text": text,
                    "page_number": meta.get("page_number", 1),
                    "file_name": meta.get("file_name", "")
                })
        chunks.sort(key=lambda x: x["page_number"])
        return chunks
