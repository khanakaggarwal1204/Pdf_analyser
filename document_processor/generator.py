import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def generate_answer(question, chunks):
    context = "\n\n".join(chunks)

    print("\n========== CONTEXT SENT TO GEMINI ==========\n")
    print(context)
    print("\n============================================\n")

    prompt = f"""
You are answering questions ONLY from the provided document.

If the document contains enough information, answer the question.
If not, reply exactly:
"The answer is not available in the provided document."

Document:
{context}

Question:
{question}

Answer:
"""

    response = client.models.generate_content(
        model="models/gemini-flash-latest",
        contents=prompt
    )

    print("\n========== GEMINI RESPONSE ==========\n")
    print(response.text)
    print("\n=====================================\n")

    return response.text