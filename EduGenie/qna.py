"""Question answering with Gemini."""
from gemini_client import generate_text


def answer_question_with_gemini(question: str) -> str:
    prompt = (
        "You are EduGenie, a friendly AI tutor. Answer the student's question "
        "accurately and concisely in simple language (a short paragraph, or a few "
        "bullet points if that is clearer).\n\n"
        f"Question: {question}"
    )
    return generate_text(prompt)
