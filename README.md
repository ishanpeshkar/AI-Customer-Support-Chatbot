# 🤖 InnovateTech — AI Customer Support Bot

> A production-grade, full-stack chatbot demonstrating robust session management, high-accuracy RAG (Retrieval-Augmented Generation), escalation simulation, conversation summarization, and deep LLM integration.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge\&logo=fastapi\&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=for-the-badge\&logo=postgresql\&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-20.10+-2496ED?style=for-the-badge\&logo=docker\&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=for-the-badge\&logo=javascript\&logoColor=black)

---

## 🎯 Project Summary

InnovateTech is a full-stack AI customer support bot designed as a professional proof-of-concept. It focuses on:

* ✅ **Conversational accuracy** using RAG (knowledge base grounding)
* ✅ **Contextual memory** via persistent sessions stored in PostgreSQL
* ✅ **LLM-powered features**: response generation, conversation summarization, and suggested next actions
* ✅ **Escalation simulation** for human handoffs
* ✅ **A modern, deployable single-file frontend** with a floating, expandable chat widget

This README contains an easy Quick Start, API examples, prompt guidance, deployment notes, and recommended next steps for production hardening.

---

### 🎥 Live Demo

**[Watch the 3-Minute Video Demo Here]**(https://drive.google.com/file/d/10QHK-pePmT1Kgj5eMa1K2gekwcXTnrwb/view?usp=sharing)

---

## 📚 Table of contents

* [Quick Start](#-quick-start)

  * [Prerequisites](#prerequisites)
  * [Clone & configure](#clone--configure)
  * [Run with Docker Compose](#run-with-docker-compose)
  * [Launch frontend](#launch-frontend)
* [How it works (high level)](#how-it-works-high-level)
* [API Reference](#api-reference)
* [Knowledge Base & RAG](#knowledge-base--rag)
* [Prompt Engineering](#prompt-engineering)
* [Future Enhancements](#future-enhancements)
* [Production checklist & additional requirements](#production-checklist--additional-requirements)
* [Troubleshooting](#troubleshooting)
* [Credits & Contact](#credits--contact)

---

## 🚀 Quick Start

### Prerequisites

* Docker & Docker Compose
* A Google AI / Gemini API Key (or other LLM provider key if you adapt the handler)
* Git (optional but recommended)

### Clone & configure

```bash
git clone https://github.com/[YOUR-USERNAME]/ai-customer-support-bot.git
cd ai-customer-support-bot
```

Create a `.env` from the example and add your keys:

```bash
cp .env.example .env
# then open .env and set:
# GOOGLE_API_KEY="YOUR_SECRET_API_KEY_HERE"
```

> 🔐 **Security note:** Do not commit `.env`. Use a secrets manager for production.

### Run with Docker Compose

Build and run backend + DB with a single command:

```bash
docker-compose up --build
```

* Backend: `http://127.0.0.1:8000`
* API docs (interactive): `http://127.0.0.1:8000/docs`

### Launch the frontend

Open the single-file frontend at `frontend/index.html` directly, or serve it with a static server (recommended):

```bash
cd frontend
npx serve -p 5173    # or: python -m http.server 5173
# open http://localhost:5173
```

Make sure `API_BASE` in the frontend points to your backend host (default: `http://127.0.0.1:8000`).

---

## 🔎 How it works (high level)

1. **Frontend** (single `index.html`) provides a floating, expandable chat widget. On first message the frontend calls `POST /api/sessions/` to create a session and stores `session_id` in `localStorage`.

2. **Backend (FastAPI)** handles REST endpoints:

   * `POST /api/sessions/` → create session
   * `POST /api/sessions/{session_id}/messages/` → receive user message, save it, run RAG + LLM to produce bot reply, save bot message
   * `POST /api/sessions/{session_id}/summarize` → instruct LLM to summarize the session and save the result

3. **Database (PostgreSQL)** stores `sessions` and `messages` (sender, content, timestamp). The conversation history is used to provide contextual memory.

4. **RAG pipeline** scans `knowledge_base.json` for matching FAQ entries and injects those facts into the LLM prompt to guarantee grounded answers.

5. **LLM handler** (provider-agnostic) communicates with Google Gemini / OpenAI based on configuration and returns structured responses.

---

## 🧭 API Reference (examples)

> All endpoints live under `/api` by default. Replace host/port if needed.

### Create a session

```http
POST /api/sessions/
Content-Type: application/json

# Response (201)
{ "id": 1 }
```

### Post a message (gets bot response)

```http
POST /api/sessions/1/messages/
Content-Type: application/json

{ "content": "Hi, how can I track my order?" }

# Response (200)
{
  "id": 2,
  "content": "You can track your order by visiting ...",
  "sender": "bot"
}
```

### Summarize a session

```http
POST /api/sessions/1/summarize
Content-Type: application/json

# Response (200)
{
  "session_id": 1,
  "summary": "User asked about returns and order tracking; bot provided FAQ-based answers and recommended escalation for account issues."
}
```

---

## 📚 Knowledge Base & RAG

`knowledge_base.json` contains an array of `faqs` objects with this structure:

```json
{
  "question": "return policy",
  "keywords": ["return", "refund", "30-day"],
  "answer": "InnovateTech offers a 30-day, no-questions-asked money-back guarantee..."
}
```

**RAG behaviour:** The backend searches for FAQ entries whose keywords match the user query (or uses a semantic search if you upgrade). Matching `answer` text is placed in the prompt as **context** so the LLM grounds its answer.

---

## 🧠 Prompt Engineering (short guide)

Use carefully designed prompts to control persona and behavior.

### RAG System Prompt (example)

```
SYSTEM:
You are a friendly and highly knowledgeable customer support assistant for InnovateTech. Use the following context verbatim if it is relevant.
--- CONTEXT FROM KNOWLEDGE BASE ---
{context_from_kb}
USER:
{user_message}
```

### Summarization Prompt (example)

```
Please analyze the following customer support conversation and provide a concise, one-paragraph summary describing the issue and the final resolution or next steps.
--- CONVERSATION TRANSCRIPT ---
{transcript}
```

**Tip:** Keep system prompts short but explicit. Always instruct the model how to use or ignore the provided context.

---

## 🔮 Future Enhancements (recommended)

* **Semantic RAG:** Replace keyword matching with vector-based semantic search (Chroma, Pinecone, Weaviate).
* **User Authentication:** Add JWT-based auth to associate sessions with user accounts and pull personalized data (orders, subscriptions).
* **Admin Dashboard:** A manager UI to review conversations, edit the knowledge base, and re-run summaries.
* **Async workers & queueing:** Offload LLM calls to worker queues for better throughput and retries.
* **Monitoring & observability:** Add tracing (OpenTelemetry), structured logs, and usage/cost monitoring for LLM API calls.

---

## 🛡️ Production checklist & additional requirements

### Infrastructure

* TLS / HTTPS (Let's Encrypt)
* Managed DB with backups (RDS / Cloud SQL)
* Secrets manager for API keys (Vault / AWS Secrets Manager / GitHub Secrets)
* Reverse proxy (Nginx / Traefik) for routing and protection

### Application

* Rate limiting and caching for frequent queries
* PII redaction before sending to external LLMs
* Data retention & deletion endpoints for compliance (GDPR/CCPA)

### Scaling

* Docker Compose for quick demos; Kubernetes for production scaling
* Use a vector DB for semantic search at scale
* Autoscaling and worker pools for LLM request handling

---

## 🩺 Troubleshooting

* **500 on LLM call:** Verify your API key, billing, and LLM provider availability. Check backend logs (`docker-compose logs -f backend`).
* **Frontend cannot reach API:** Ensure `API_BASE` is correct and backend allows CORS.
* **DB connection refused:** Check `DATABASE_URL` and that Postgres is running (`docker-compose ps`).
* **Session issues:** Clear browser `localStorage.chat_session_id` to reset a session.

---

## 📁 Suggested `.env.example`

```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/innovate
LLM_PROVIDER=google_gemini
GOOGLE_API_KEY=REPLACE_ME
OPENAI_API_KEY=REPLACE_ME
DEBUG=true
PORT=8000
```

---

## 📦 Deployment recommendations

* For staging: Docker Compose on a small VM, fronted by Nginx/Traefik with TLS.
* For production: Kubernetes, managed DB, separate worker pool, vector DB for RAG, CI/CD pipeline, and secrets manager.

---

## 🙋‍♂️ Credits & Contact

* **Author:** `Your Name` — `you@example.com`
* **Repo:** `https://github.com/[YOUR-USERNAME]/ai-customer-support-bot`
* **License:** MIT

---

> Want help customizing this README (badges, video link, or repo URL inserted)? Tell me what to add and I’ll update the file.
