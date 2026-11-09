from document_processor.database import collection


def store_embeddings(embedded_chunks):
    # Preserve previous documents in the persistent collection.
    # Each chunk has a globally unique ID generated during upload.

    for chunk in embedded_chunks:
        collection.add(
            ids=[str(chunk["id"])],
            embeddings=[chunk["embedding"]],
            documents=[chunk["text"]],
            metadatas=[
                {
                    "source": chunk["source"],
                    "document_id": chunk.get("document_id", "")
                }
            ]
        )

    return collection
