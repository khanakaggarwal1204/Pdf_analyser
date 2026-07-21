def ask_rag(question: str, session_id: str):
    """
    Placeholder for the AI/RAG pipeline.

    Later, this function will call Student 3's
    LangChain + ChromaDB pipeline.
    """

    return {
        "answer": f"AI Response for: {question}",
        "sources": [
            {
                "document": "Sample Document",
                "page": 1
            }
        ]
    }
