from document_processor.read_pdf import extract_pdf_text
from document_processor.clean_text import clean_text
from document_processor.chunk_text import chunk_text
from document_processor.metadata import add_metadata
from document_processor.embeddings import create_embeddings
from document_processor.vector_store import store_embeddings
from document_processor.retriever import retrieve_chunks
from document_processor.generator import generate_answer

DEBUG = False

def main():
    pdf_path = "data/Sample_data.pdf"
    question = input("Enter your question: ")
    
    text = extract_pdf_text(pdf_path)

    if not text.strip():
        print("Could not extract text from the PDF.")
        return

    cleaned_text = clean_text(text)
    chunks = chunk_text(cleaned_text)

    chunk_data = add_metadata(chunks, pdf_path)

    embedded_chunks = create_embeddings(chunk_data)

    store_embeddings(embedded_chunks)

    results = retrieve_chunks(question)

    if not results["documents"] or not results["documents"][0]:
        print("No relevant information found.")
        return

    retrieved_chunks=results["documents"][0]

    if DEBUG:
        print("\n---Retrieved Chunks---\n")
        for i, doc in enumerate(retrieved_chunks, start=1):
            print(f"\nChunk {i}:")
            print(doc)
            print("-" * 60)

    print("\nGenerating answer...\n")
    answer = generate_answer(question, retrieved_chunks)

    print("\n---Answer---\n")
    print(answer)


if __name__ == "__main__":
    main()