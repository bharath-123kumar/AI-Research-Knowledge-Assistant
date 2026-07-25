from typing import List, Dict, Any
from config.settings import settings

class RecursiveChunker:
    """
    Intelligent Recursive Chunker that splits text into context-rich overlapping segments.
    Justification: Overlapping segments (~150 chars) ensure semantic continuity across split boundaries
    so that citations and answers don't lose context.
    """
    def __init__(self, chunk_size: int = settings.CHUNK_SIZE, chunk_overlap: int = settings.CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def create_chunks(self, pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Splits page text into overlapping chunks while preserving page metadata."""
        chunks = []
        global_chunk_idx = 0

        for page in pages_data:
            text = page["text"]
            start = 0
            text_length = len(text)

            while start < text_length:
                end = start + self.chunk_size
                chunk_text = text[start:end].strip()

                if chunk_text:
                    chunks.append({
                        "chunk_id": f"{page['doc_id']}_c{global_chunk_idx}",
                        "doc_id": page["doc_id"],
                        "file_name": page["file_name"],
                        "page_number": page["page_number"],
                        "text": chunk_text
                    })
                    global_chunk_idx += 1

                start += (self.chunk_size - self.chunk_overlap)
                if start >= text_length:
                    break

        return chunks
