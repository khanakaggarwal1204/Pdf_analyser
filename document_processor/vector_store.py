from document_processor.database import collection

def store_embeddings(embedded_chunks):
    if collection.count()>0:
        collection.delete(
            ids=collection.get()["ids"]
        )
    for chunk in embedded_chunks:
        collection.add(
            ids=[str(chunk["id"])],
            embeddings=[chunk["embedding"]],
            documents=[chunk["text"]],
            metadatas=[
                {
                    "source":chunk["source"]
                }
            ]
        )
    return collection