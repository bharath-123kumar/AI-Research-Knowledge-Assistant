import pytest
import os
from src.document_processing.pdf_parser import PDFParser
from src.document_processing.chunker import RecursiveChunker
from src.ml.predictor import DocumentClassifier

def test_pdf_parsing_and_chunking():
    sample_pdf = "sample_documents/sample_ai_paper.pdf"
    assert os.path.exists(sample_pdf), "Sample PDF should exist"

    parser = PDFParser()
    pages = parser.extract_pages(sample_pdf, "test_doc_1", "sample_ai_paper.pdf")
    assert len(pages) > 0
    assert pages[0]["page_number"] == 1
    assert "artificial intelligence" in pages[0]["text"].lower()

    chunker = RecursiveChunker(chunk_size=300, chunk_overlap=50)
    chunks = chunker.create_chunks(pages)
    assert len(chunks) >= 1
    assert chunks[0]["doc_id"] == "test_doc_1"

def test_tf_classifier_inference():
    classifier = DocumentClassifier()
    sample_text = "Deep neural networks trained with backpropagation process image arrays for computer vision and object detection."
    res = classifier.predict(sample_text)
    
    assert "category" in res
    assert "confidence" in res
    assert res["category"] in [
        "Artificial Intelligence", "Machine Learning", "Computer Vision",
        "Natural Language Processing", "Robotics", "Cyber Security", "Cloud Computing"
    ]
