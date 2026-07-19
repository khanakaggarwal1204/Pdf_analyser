from document_processor.read_pdf import extract_pdf_text
from document_processor.clean_text import clean_text
from document_processor.chunk_text import chunk_text
from document_processor.metadata import add_metadata
from document_processor.embeddings import create_embeddings
from document_processor.vector_store import store_embeddings
from document_processor.retriever import retrieve_chunks

def main():
    pdf_path="data/Sample_data.pdf"
    question="What is NumPy?"
    text=extract_pdf_text(pdf_path)
    cleaned_text=clean_text(text)
    chunks=chunk_text(cleaned_text)

    chunk_data=add_metadata(chunks, pdf_path)
    embedded_chunks=create_embeddings(chunk_data)

    vector_db=store_embeddings(embedded_chunks)
    results=retrieve_chunks(question)

    print("\n---Statistics---")
    print(f"Characters   : {len(cleaned_text)}")
    print(f"Chunks       : {len(chunks)}")

    print("\n---First Chunk:---")
    print(f"ID           :{embedded_chunks[0]['id']}")
    print(f"Source       :{embedded_chunks[0]['source']}")
    print(f"Text         :{embedded_chunks[0]['text'][:200]}...")

    print("\n---Embedding---")
    print(f"Keys         :{list(embedded_chunks[0].keys())}")
    print(f"Dimensions   :{len(embedded_chunks[0]["embedding"])}")

    print("\nStored Successfully!")
    print(f"Vectors Stored: {vector_db.count()}")

    print("\n---Retrieved Chunks---\n")
    for i, doc in enumerate(results['documents'][0], start=1):
        print(f'Chunk {i}:')
        print(doc)
        print("-" * 50)

if __name__=="__main__":
    main()
