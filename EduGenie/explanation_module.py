"""Concept explanation.

Default: the local LaMini-Flan-T5-783M model (lazy-loaded on the first request so
the server starts instantly). If EXPLAIN_BACKEND=gemini, or the local model cannot
be loaded (not installed / no internet), Gemini is used instead.
"""
import threading

import config
from gemini_client import generate_text

_tokenizer = None
_model = None
_load_lock = threading.Lock()


def _load_local_model():
    global _tokenizer, _model
    with _load_lock:
        if _model is None:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

            print(f"Loading local model {config.LOCAL_EXPLAIN_MODEL} (first use may take a while)...")
            _tokenizer = AutoTokenizer.from_pretrained(config.LOCAL_EXPLAIN_MODEL)
            _model = AutoModelForSeq2SeqLM.from_pretrained(config.LOCAL_EXPLAIN_MODEL)
            _model.eval()
    return _tokenizer, _model


def _explain_local(topic: str) -> str:
    import torch

    tokenizer, model = _load_local_model()
    input_text = f"Explain the concept of '{topic}' in a simple and clear way for a school student."
    inputs = tokenizer(input_text, return_tensors="pt")
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            temperature=0.7,
            top_k=50,
            top_p=0.95,
            do_sample=True,
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True).strip()


def _explain_gemini(topic: str) -> str:
    prompt = (
        f"Explain the concept of '{topic}' in a simple and clear way for a school student. "
        "Use easy words and a short everyday example. Keep it under 150 words."
    )
    return generate_text(prompt)


def explain_topic(topic: str) -> str:
    if config.EXPLAIN_BACKEND == "gemini":
        return _explain_gemini(topic)
    try:
        return _explain_local(topic)
    except Exception as exc:  # missing torch/transformers, download failure, out of memory...
        print(f"Local explanation model unavailable ({exc!r}); falling back to Gemini.")
        return _explain_gemini(topic)
