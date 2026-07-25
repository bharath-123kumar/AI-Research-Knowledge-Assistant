import fitz # PyMuPDF

def create_sample_pdfs():
    # 1. Artificial Intelligence PDF
    doc1 = fitz.open()
    page1 = doc1.new_page()
    page1.insert_text(
        fitz.Point(50, 50),
        "AI Research Paper: Autonomous Multi-Agent Systems\n\n"
        "Abstract:\n"
        "This research paper presents an enterprise framework for autonomous multi-agent cognitive systems. "
        "Artificial Intelligence agents leverage heuristic decision models, symbolic logic graphs, and neural reasoning engines "
        "to solve multi-step domain planning problems.\n\n"
        "1. Introduction:\n"
        "Modern artificial intelligence architectures focus on distributed problem solving. Heuristic search algorithms "
        "allow autonomous agents to coordinate actions in complex environments. Symbolic reasoning models provide strict control safety.\n\n"
        "2. Experimental Results:\n"
        "Our multi-agent system achieved 94.2% task efficiency in enterprise benchmark evaluations."
    )
    doc1.save("sample_documents/sample_ai_paper.pdf")
    doc1.close()

    # 2. Cyber Security PDF
    doc2 = fitz.open()
    page1 = doc2.new_page()
    page1.insert_text(
        fitz.Point(50, 50),
        "Technical Whitepaper: Zero-Trust Cyber Security Architecture\n\n"
        "Abstract:\n"
        "This paper details enterprise implementation strategies for Zero-Trust cyber security networks. "
        "It evaluates cryptographic end-to-end encryption protocols, micro-segmentation, identity access management, and automated intrusion detection systems.\n\n"
        "1. Threat Prevention Framework:\n"
        "Cyber security mechanisms require real-time intrusion monitoring. Packet inspection algorithms evaluate perimeter risks. "
        "Continuous authentication prevents unauthorized lateral movement in cloud infrastructure.\n\n"
        "2. Conclusion:\n"
        "Zero-Trust network architecture reduces security vulnerability surface area by 78%."
    )
    doc2.save("sample_documents/sample_security_paper.pdf")
    doc2.close()

    print("Created sample PDF documents in sample_documents/")

if __name__ == "__main__":
    create_sample_pdfs()
