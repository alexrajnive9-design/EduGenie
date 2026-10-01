# EduGenie: Google Gemini Powered Learning Assistant

A lightweight AI study assistant built with **FastAPI** + a plain **HTML/CSS/JS** frontend.

| Feature | Endpoint | Powered by |
|---|---|---|
| Ask questions | `GET /qa?question=...` | Gemini |
| Explain a concept | `POST /explain` `{"topic": "..."}` | LaMini-Flan-T5-783M (local), falls back to Gemini |
| Generate a quiz (3 MCQs x 4 options) | `POST /quiz` `{"text": "..."}` | Gemini |
| Summarize text | `POST /summarize` `{"text": "..."}` | Gemini |
| Learning path | `GET /learn/recommendations?topic=...` | Gemini |

## Project structure

```
EduGenie/
├── main.py                 # FastAPI app + routes
├── config.py               # Reads settings from .env
├── gemini_client.py        # Shared Gemini wrapper + error handling
├── explanation_module.py   # Concept explanation (local model, Gemini fallback)
├── qna.py                  # Question answering
├── quiz_module.py          # Quiz generation + JSON validation
├── summary_module.py       # Summarization
├── learning_path.py        # Learning recommendations
├── templates/index.html    # Frontend page
├── static/style.css        # Styling
├── static/app.js           # Frontend logic (calls the API, renders results)
├── tests/                  # Automated tests (no API key needed)
├── .vscode/                # VS Code debug + test settings
├── .env.example            # Copy to .env and add your key
└── requirements.txt
```

## 1. Prerequisites

- **Python 3.10 or newer**: check with `python --version` (use `python3` on macOS/Linux).
  On Windows, tick **"Add Python to PATH"** in the installer.
- **VS Code** with the **Python** extension (Microsoft).
- A **free Gemini API key**: sign in at <https://aistudio.google.com/app/apikey> and click **Create API key**.

## 2. Setup in VS Code

1. **File > Open Folder...** and choose the `EduGenie` folder.
2. Open the terminal: **Terminal > New Terminal**.
3. Create and activate a virtual environment:

   **macOS / Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
   **Windows (PowerShell)**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
   (If PowerShell blocks the script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or use Command Prompt: `.venv\Scripts\activate.bat`.)

4. When VS Code asks about the new environment, click **Yes**. Otherwise press `Ctrl+Shift+P` (`Cmd+Shift+P` on Mac), run **Python: Select Interpreter**, and pick the one inside `.venv`.
5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   > `torch` and `transformers` are large (a few GB). If you only want Gemini and no local model, skip them: delete those three lines from `requirements.txt` first and set `EXPLAIN_BACKEND=gemini` below.
6. Create your settings file:
   ```bash
   cp .env.example .env          # Windows: copy .env.example .env
   ```
   Open `.env` and paste your key: `GEMINI_API_KEY=AIza...`

## 3. Run the app

```bash
uvicorn main:app --reload
```

Open <http://127.0.0.1:8000> in your browser. Press `Ctrl+C` in the terminal to stop.

You can also press **F5** in VS Code (Run and Debug > "EduGenie: FastAPI (uvicorn)") to run with the debugger.

Interactive API docs: <http://127.0.0.1:8000/docs>
Quick status check: <http://127.0.0.1:8000/health> (confirms your key and model are loaded).

> **First "Explain" request:** with `EXPLAIN_BACKEND=local`, the LaMini-Flan-T5-783M model (~3 GB) downloads and loads on first use, so that one request can take a few minutes. Later requests are fast. Set `EXPLAIN_BACKEND=gemini` in `.env` to skip the download entirely.

## 4. Test it

**In the browser** (pick a task from the dropdown):

| Task | Try |
|---|---|
| Ask a Question | `Which is the largest ocean?` |
| Explain a Concept | `Photosynthesis` |
| Generate Quiz | `The Pythagoras Theorem` (3 questions; wrong answers show the correct one) |
| Summarize Text | paste any long paragraph |
| Recommend Learning Path | `SQL` |

**From the terminal** (macOS/Linux/Git Bash):

```bash
curl "http://127.0.0.1:8000/qa?question=Which%20is%20the%20largest%20ocean%3F"
curl -X POST http://127.0.0.1:8000/explain  -H "Content-Type: application/json" -d '{"topic":"Photosynthesis"}'
curl -X POST http://127.0.0.1:8000/summarize -H "Content-Type: application/json" -d '{"text":"Paste a long passage here"}'
curl -X POST http://127.0.0.1:8000/quiz      -H "Content-Type: application/json" -d '{"text":"Pythagoras Theorem"}'
curl "http://127.0.0.1:8000/learn/recommendations?topic=SQL"
```

**Automated tests** (Gemini and the local model are mocked, so no key or download needed):

```bash
pytest
```

## Configuration (`.env`)

| Variable | Default | Meaning |
|---|---|---|
| `GEMINI_API_KEY` | none | Your Google AI Studio key (required for everything except local explanations) |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model name |
| `EXPLAIN_BACKEND` | `local` | `local` = LaMini-Flan-T5, `gemini` = use Gemini |

## Troubleshooting

| Problem | Fix |
|---|---|
| `GEMINI_API_KEY is not set` shown in the page | Create `.env` (step 6), add the key, restart `uvicorn`. |
| `404 ... model not found` | Google retires old models. The original document's `gemini-1.5-pro` no longer works. Set `GEMINI_MODEL` in `.env` to a current model from <https://ai.google.dev/gemini-api/docs/models> and restart. |
| `429 / quota exceeded` | You hit the free-tier rate limit. Wait a minute, or switch to a lighter model. |
| `uvicorn` is not recognized | The virtual environment isn't active. Re-run the activate command from step 3. |
| Explain is very slow or runs out of memory | Set `EXPLAIN_BACKEND=gemini` in `.env`. |
| Quiz says it couldn't build a valid quiz | The model returned malformed JSON twice. Click Generate Quiz again, or give it a longer passage. |
| Port 8000 already in use | `uvicorn main:app --reload --port 8001` |
