"""Personalized learning path recommendations with Gemini."""
from gemini_client import generate_text


def get_learning_recommendations(topic: str) -> str:
    prompt = f"""
You are an AI tutor. The student wants to learn about: {topic}.
Suggest a structured and adaptive learning path including key topics, order of
learning, approximate timelines, and resources (links, videos, articles, books).
Include beginner, intermediate, and advanced levels if needed.
Use clear headings and bullet points, and finish with a few adaptive learning tips.
"""
    return generate_text(prompt)
