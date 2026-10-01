"""API tests. Gemini and the local model are mocked, so no key or download is needed."""
import pytest
from fastapi.testclient import TestClient

import main
from gemini_client import GeminiError


@pytest.fixture()
def client():
    return TestClient(main.app)


def test_home_page_served(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "EduGenie" in r.text


def test_static_files_served(client):
    assert client.get("/static/style.css").status_code == 200
    assert client.get("/static/app.js").status_code == 200


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_qa(client, monkeypatch):
    monkeypatch.setattr(main, "answer_question_with_gemini", lambda q: "Pacific Ocean")
    r = client.get("/qa", params={"question": "Which is the largest ocean?"})
    assert r.status_code == 200
    assert r.json() == {"answer": "Pacific Ocean"}


def test_qa_missing_question(client):
    assert client.get("/qa").status_code == 400


def test_explain(client, monkeypatch):
    monkeypatch.setattr(main, "explain_topic", lambda t: f"About {t}")
    for path in ("/explain", "/explain/"):
        r = client.post(path, json={"topic": "Photosynthesis"})
        assert r.status_code == 200
        assert r.json() == {"topic": "Photosynthesis", "explanation": "About Photosynthesis"}


def test_explain_empty_topic(client):
    r = client.post("/explain", json={"topic": "   "})
    assert r.status_code == 400
    assert "topic" in r.json()["error"].lower()


def test_summarize(client, monkeypatch):
    monkeypatch.setattr(main, "summarize_text", lambda t: "short")
    r = client.post("/summarize", json={"text": "a long passage"})
    assert r.json() == {"summary": "short"}


def test_summarize_empty(client):
    assert client.post("/summarize/", json={}).status_code == 400


def test_quiz(client, monkeypatch):
    fake = [{"question": "Q?", "options": ["a", "b", "c", "d"], "answer": "a"}]
    monkeypatch.setattr(main, "generate_quiz", lambda t: fake)
    r = client.post("/quiz", json={"text": "Pythagoras Theorem"})
    assert r.json() == {"quiz": fake}


def test_quiz_empty(client):
    assert client.post("/quiz", json={"text": ""}).status_code == 400


def test_learning_recommendations(client, monkeypatch):
    monkeypatch.setattr(main, "get_learning_recommendations", lambda t: "plan")
    r = client.get("/learn/recommendations", params={"topic": "SQL"})
    assert r.json() == {"topic": "SQL", "recommendation": "plan"}


def test_gemini_failure_becomes_clean_502(client, monkeypatch):
    def boom(_):
        raise GeminiError("GEMINI_API_KEY is not set.")

    monkeypatch.setattr(main, "answer_question_with_gemini", boom)
    r = client.get("/qa", params={"question": "hi"})
    assert r.status_code == 502
    assert "GEMINI_API_KEY" in r.json()["error"]
