"use strict";

const TASKS = {
  qa:      { label: "Your question:",             placeholder: "Which is the largest ocean?",                  button: "Get Answer" },
  explain: { label: "Concept to explain:",        placeholder: "Photosynthesis",                               button: "Explain" },
  quiz:    { label: "Topic or passage:",          placeholder: "Pythagoras Theorem (or paste a passage here)", button: "Generate Quiz" },
  summary: { label: "Text to summarize:",         placeholder: "Paste a long paragraph here...",               button: "Summarize" },
  path:    { label: "What do you want to learn?", placeholder: "SQL",                                          button: "Recommend Path" },
};

const form = document.getElementById("eduForm");
const taskSelect = document.getElementById("task");
const input = document.getElementById("userInput");
const inputLabel = document.getElementById("inputLabel");
const submitBtn = document.getElementById("submitBtn");
const resultBox = document.getElementById("result");
const resultTitle = document.getElementById("resultTitle");
const resultBody = document.getElementById("resultBody");

function applyTask() {
  const t = TASKS[taskSelect.value];
  inputLabel.textContent = "";
  const strong = document.createElement("strong");
  strong.textContent = t.label;
  inputLabel.appendChild(strong);
  input.placeholder = t.placeholder;
  submitBtn.textContent = t.button;
}
taskSelect.addEventListener("change", applyTask);
applyTask();

// ---------- tiny, safe Markdown renderer (escapes HTML first) ----------
function escapeHtml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
          .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

function inlineMd(s) {
  s = escapeHtml(s);
  s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
                '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
  s = s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  s = s.replace(/(^|[^*])\*(?!\s)([^*]+?)\*(?!\*)/g, "$1<em>$2</em>");
  return s;
}

function renderMarkdown(text) {
  const lines = String(text).replace(/\r\n/g, "\n").split("\n");
  let html = "";
  let inList = false;

  const closeList = () => { if (inList) { html += "</ul>"; inList = false; } };

  for (const raw of lines) {
    const line = raw.replace(/\s+$/, "");
    if (!line.trim()) { closeList(); continue; }

    const heading = line.match(/^\s{0,3}(#{1,4})\s+(.*)$/);
    if (heading) {
      closeList();
      const tag = heading[1].length <= 2 ? "h3" : "h4";
      html += `<${tag}>${inlineMd(heading[2])}</${tag}>`;
      continue;
    }

    const item = line.match(/^(\s*)([*\-+]|\d+[.)])\s+(.*)$/);
    if (item) {
      if (!inList) { html += "<ul>"; inList = true; }
      const level = Math.min(2, Math.floor(item[1].replace(/\t/g, "    ").length / 4));
      html += `<li class="indent-${level}">${inlineMd(item[3])}</li>`;
      continue;
    }

    closeList();
    html += `<p>${inlineMd(line.trim())}</p>`;
  }
  closeList();
  return html;
}

// ---------- UI helpers ----------
function showResult(title) {
  resultTitle.textContent = title;
  resultBox.classList.remove("hidden");
}
function showLoading() {
  showResult("Working on it...");
  resultBody.innerHTML =
    '<p class="loading">EduGenie is thinking... (the first local explanation can take a while as the model loads)</p>';
}
function showError(message) {
  showResult("Something went wrong");
  resultBody.innerHTML = "";
  const div = document.createElement("div");
  div.className = "error";
  div.textContent = message;
  resultBody.appendChild(div);
}
function showMarkdown(title, text) {
  showResult(title);
  resultBody.innerHTML = renderMarkdown(text);
}

// ---------- Quiz rendering ----------
function renderQuiz(quiz) {
  showResult("Quiz");
  resultBody.innerHTML = "";
  let answered = 0;
  let correctCount = 0;
  const scoreEl = document.createElement("div");
  scoreEl.className = "score";

  quiz.forEach((q, qi) => {
    const wrap = document.createElement("div");
    wrap.className = "question";

    const qText = document.createElement("div");
    qText.className = "q-text";
    qText.textContent = `${qi + 1}. ${q.question}`;
    wrap.appendChild(qText);

    const feedback = document.createElement("div");
    const buttons = [];

    q.options.forEach((opt) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "option";
      btn.textContent = opt;
      btn.addEventListener("click", () => {
        buttons.forEach((b) => { b.disabled = true; });
        const isRight = opt === q.answer;
        btn.classList.add(isRight ? "correct" : "wrong");
        if (isRight) {
          correctCount++;
          feedback.className = "feedback good";
          feedback.textContent = "✅ Correct!";
        } else {
          const right = buttons.find((b) => b.textContent === q.answer);
          if (right) right.classList.add("correct");
          feedback.className = "feedback bad";
          feedback.textContent = `❌ Not quite. The correct answer is: ${q.answer}`;
        }
        answered++;
        if (answered === quiz.length) {
          scoreEl.textContent = `Your score: ${correctCount} / ${quiz.length}`;
        }
      });
      buttons.push(btn);
      wrap.appendChild(btn);
    });

    wrap.appendChild(feedback);
    resultBody.appendChild(wrap);
  });

  resultBody.appendChild(scoreEl);
}

// ---------- API calls ----------
async function callApi(url, options) {
  let response;
  try {
    response = await fetch(url, options);
  } catch (e) {
    throw new Error("Cannot reach the EduGenie server. Is it running?");
  }
  let data = {};
  try { data = await response.json(); } catch (e) { /* non-JSON error body */ }
  if (!response.ok) {
    throw new Error(data.error || `Server error (${response.status}).`);
  }
  return data;
}

const postJson = (url, body) => callApi(url, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const value = input.value.trim();
  if (!value) return;

  const task = taskSelect.value;
  submitBtn.disabled = true;
  showLoading();

  try {
    if (task === "qa") {
      const data = await callApi(`/qa?question=${encodeURIComponent(value)}`);
      showMarkdown("Answer", data.answer);
    } else if (task === "explain") {
      const data = await postJson("/explain", { topic: value });
      showMarkdown(`Explanation: ${data.topic}`, data.explanation);
    } else if (task === "summary") {
      const data = await postJson("/summarize", { text: value });
      showMarkdown("Summary", data.summary);
    } else if (task === "quiz") {
      const data = await postJson("/quiz", { text: value });
      renderQuiz(data.quiz);
    } else if (task === "path") {
      const data = await callApi(`/learn/recommendations?topic=${encodeURIComponent(value)}`);
      showMarkdown(`Learning Path: ${data.topic}`, data.recommendation);
    }
  } catch (err) {
    showError(err.message);
  } finally {
    submitBtn.disabled = false;
  }
});
