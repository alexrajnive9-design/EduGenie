"""Quiz generation with Gemini (3 MCQs, 4 options each, JSON output)."""
import json
import re

from gemini_client import GeminiError, generate_text


def clean_json_block(text: str) -> str:
    """Remove Markdown ```json code fences if the model added them."""
    return re.sub(r"```(?:json)?\s*(.*?)```", r"\1", text, flags=re.DOTALL).strip()


def _validate(raw) -> list:
    """Check the parsed JSON has 3 questions x 4 options with a matching answer."""
    if isinstance(raw, dict):  # tolerate {"questions": [...]} or {"quiz": [...]}
        raw = raw.get("questions") or raw.get("quiz") or []
    if not isinstance(raw, list) or len(raw) < 1:
        raise ValueError("Quiz is not a list of questions.")

    quiz = []
    for item in raw[:3]:
        question = str(item.get("question", "")).strip()
        options = [str(o).strip() for o in item.get("options", [])]
        answer = str(item.get("answer", "")).strip()
        if not question or len(options) != 4:
            raise ValueError("Each question needs text and exactly 4 options.")
        if answer not in options:
            # Accept a letter answer like "B" or "B)" and map it to the option
            letter = answer[:1].upper()
            if len(answer) <= 2 and letter in "ABCD":
                answer = options["ABCD".index(letter)]
            else:
                raise ValueError("Answer does not match any option.")
        quiz.append({"question": question, "options": options, "answer": answer})
    return quiz


def generate_quiz(text: str) -> list:
    prompt = f"""
You are a quiz generator.

From the following passage or topic, create 3 multiple-choice questions. Each question should include:
- A "question"
- A list of 4 "options"
- A correct "answer" that must exactly match one of the options.

Format your output as **valid JSON**, like this:
[
  {{
    "question": "What is ...?",
    "options": ["A", "B", "C", "D"],
    "answer": "A"
  }}
]

Return only the JSON, nothing else.

Passage:
{text}
"""
    last_error = None
    for _ in range(2):  # one retry if the model returns malformed JSON
        quiz_text = generate_text(prompt, json_output=True)
        try:
            return _validate(json.loads(clean_json_block(quiz_text)))
        except (ValueError, TypeError, AttributeError) as exc:  # JSONDecodeError is a ValueError
            last_error = exc
    raise GeminiError(f"Could not build a valid quiz from the model output: {last_error}")
