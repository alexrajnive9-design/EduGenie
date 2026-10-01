"""EduGenie - Google Gemini powered learning assistant (FastAPI backend).

Run with:  uvicorn main:app --reload
"""
from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import config
from explanation_module import explain_topic
from gemini_client import GeminiError
from learning_path import get_learning_recommendations
from qna import answer_question_with_gemini
from quiz_module import generate_quiz
from summary_module import summarize_text

app = FastAPI(title="EduGenie", description="Google Gemini powered learning assistant")

app.mount("/static", StaticFiles(directory=config.BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(config.BASE_DIR / "templates"))


# ---------- Request bodies ----------
class TopicBody(BaseModel):
    topic: str = ""


class TextBody(BaseModel):
    text: str = ""


# ---------- Error handling ----------
@app.exception_handler(GeminiError)
async def gemini_error_handler(request: Request, exc: GeminiError):
    return JSONResponse(status_code=502, content={"error": str(exc)})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "Invalid or missing input."})


# ---------- Frontend ----------
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "gemini_key_configured": bool(config.GEMINI_API_KEY)
        and config.GEMINI_API_KEY != "your_api_key_here",
        "gemini_model": config.GEMINI_MODEL,
        "explain_backend": config.EXPLAIN_BACKEND,
    }


# ---------- API routes ----------
# Q&A - GET API using Gemini
@app.get("/qa")
def answer_question(question: str = Query(..., min_length=1)):
    question = question.strip()
    if not question:
        return JSONResponse(content={"error": "Please provide a question."}, status_code=400)
    return {"answer": answer_question_with_gemini(question)}


# Explanation - POST API
@app.post("/explain")
@app.post("/explain/", include_in_schema=False)
def explain_api(body: TopicBody):
    topic = body.topic.strip()
    if not topic:
        return JSONResponse(content={"error": "Please provide a topic."}, status_code=400)
    return {"topic": topic, "explanation": explain_topic(topic)}


# Summarization - POST API
@app.post("/summarize")
@app.post("/summarize/", include_in_schema=False)
def summarize_api(body: TextBody):
    text = body.text.strip()
    if not text:
        return JSONResponse(content={"error": "Please provide text to summarize."}, status_code=400)
    return {"summary": summarize_text(text)}


# Quiz Generation - POST API
@app.post("/quiz")
@app.post("/quiz/", include_in_schema=False)
def quiz_api(body: TextBody):
    text = body.text.strip()
    if not text:
        return JSONResponse(content={"error": "Please provide text for quiz."}, status_code=400)
    return {"quiz": generate_quiz(text)}


# Learning Recommendations - GET API
@app.get("/learn/recommendations")
def learning_recommendation_api(topic: str = Query(..., min_length=1)):
    topic = topic.strip()
    if not topic:
        return JSONResponse(content={"error": "Please provide a topic."}, status_code=400)
    return {"topic": topic, "recommendation": get_learning_recommendations(topic)}
