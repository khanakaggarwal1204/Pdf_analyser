import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def generate_answer(question, chunks):
    context = "\n\n".join(chunks)

    prompt = f"""
Use only the information provided below to answer the question.
If the answer is not present in the context, reply:
"The answer is not available in the provided document."

Context:
{context}

Question:
{question}

Answer:
"""

    response = client.models.generate_content(
        model="models/gemini-flash-latest",
        contents=prompt
    )

    return response.text