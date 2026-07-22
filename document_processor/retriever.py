from document_processor.database import collection
from sentence_transformers import SentenceTransformer

model=SentenceTransformer(
    "all-MiniLM-L6-v2"
)

def retrieve_chunks(question, n_results=5):
    print("Collection count:", collection.count())

    question_embedding=model.encode(question).tolist()
    results=collection.query(
        query_embeddings=[question_embedding],
        n_results=n_results
    )
    return results