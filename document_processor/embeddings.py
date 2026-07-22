from sentence_transformers import SentenceTransformer
model=SentenceTransformer("all-MiniLM-L6-v2")
def create_embeddings(chunk_data):
    for chunk in chunk_data:
        embedding=model.encode(chunk["text"])
        chunk["embedding"]=embedding.tolist()
    return chunk_data
