import json

import pytest

import quiz_module
from gemini_client import GeminiError

GOOD = [
    {"question": f"Q{i}?", "options": ["a", "b", "c", "d"], "answer": "b"} for i in range(3)
]


def test_clean_json_block_removes_fences():
    fenced = "```json\n" + json.dumps(GOOD) + "\n```"
    assert json.loads(quiz_module.clean_json_block(fenced)) == GOOD


def test_clean_json_block_leaves_plain_json():
    assert json.loads(quiz_module.clean_json_block(json.dumps(GOOD))) == GOOD


def test_generate_quiz_happy_path(monkeypatch):
    monkeypatch.setattr(quiz_module, "generate_text", lambda p, json_output=False: json.dumps(GOOD))
    quiz = quiz_module.generate_quiz("Solar System")
    assert len(quiz) == 3
    assert all(len(q["options"]) == 4 and q["answer"] in q["options"] for q in quiz)


def test_generate_quiz_maps_letter_answer(monkeypatch):
    data = [{"question": "Q?", "options": ["w", "x", "y", "z"], "answer": "C"}]
    monkeypatch.setattr(quiz_module, "generate_text", lambda p, json_output=False: json.dumps(data))
    assert quiz_module.generate_quiz("t")[0]["answer"] == "y"


def test_generate_quiz_retries_then_succeeds(monkeypatch):
    replies = iter(["not json at all", json.dumps(GOOD)])
    monkeypatch.setattr(quiz_module, "generate_text", lambda p, json_output=False: next(replies))
    assert len(quiz_module.generate_quiz("t")) == 3


def test_generate_quiz_raises_after_two_bad_replies(monkeypatch):
    monkeypatch.setattr(quiz_module, "generate_text", lambda p, json_output=False: "garbage")
    with pytest.raises(GeminiError):
        quiz_module.generate_quiz("t")


def test_generate_quiz_rejects_wrong_option_count(monkeypatch):
    bad = [{"question": "Q?", "options": ["a", "b"], "answer": "a"}]
    monkeypatch.setattr(quiz_module, "generate_text", lambda p, json_output=False: json.dumps(bad))
    with pytest.raises(GeminiError):
        quiz_module.generate_quiz("t")
