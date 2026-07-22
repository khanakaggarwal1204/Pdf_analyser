from document_processor.read_pdf import extract_pdf_text
from document_processor.clean_text import clean_text
from document_processor.chunk_text import chunk_text
from document_processor.metadata import add_metadata
from document_processor.embeddings import create_embeddings
from document_processor.vector_store import store_embeddings
from document_processor.retriever import retrieve_chunks
from document_processor.generator import generate_answer

def main():
    pdf_path = "data/Sample_data.pdf"
    question = input("Enter your question: ")

    text = extract_pdf_text(pdf_path)
    cleaned_text = clean_text(text)
    chunks = chunk_text(cleaned_text)

    chunk_data = add_metadata(chunks, pdf_path)
    embedded_chunks = create_embeddings(chunk_data)

    collection = store_embeddings(embedded_chunks)
    results = retrieve_chunks(question)

    DEBUG = False
    if DEBUG:
        print("\n---Retrieved Chunks---\n")
        for i, doc in enumerate(results["documents"][0], start=1):
            print(f"\nChunk {i}:")
            print(doc)
            print("-" * 60)

    retrieved_chunks = results["documents"][0]
    answer = generate_answer(question, retrieved_chunks)

    print("\n---Answer---\n")
    print(answer)

if __name__ == "__main__":
    main()