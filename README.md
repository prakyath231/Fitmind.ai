# FitMind

I got tired of copy-pasting my workouts into ChatGPT every single day.

Not because ChatGPT gave bad advice — it didn't. But every conversation started from zero. It had no idea I'd been training chest twice a week for the past month, or that my bench had stalled, or that I consistently under-eat protein on days I train. I had to re-explain everything, every time.

So I built FitMind. An AI coach that actually remembers you.

---


## What it does

You talk to it like you'd text a friend:

```
"Pull day today — lat pulldown, seated row, bicep curls"
```

It knows your last pull session. It knows your weights. It tells you to go up 2.5kg on lat pulldown because you hit all your reps last time. It warns you that your shoulders haven't been trained in 9 days and suggests adding face pulls.

```
"Had chicken rice for lunch"
```

It logs it, estimates the macros, tells you you're at 52g protein with 98g still to go, and suggests what to eat for dinner based on what you usually have.

This is the thing I actually wanted. Not a generic meal plan generator. A coach that knows my data.

---

## How it works

Every time you send a message, FitMind:

1. Checks if it's a log entry — if yes, extracts the structure using Mistral and indexes it into Qdrant + BM25 in real time. No manual step.
2. If it's a question, runs hybrid search over your personal history — dense vectors for semantic meaning, BM25 for exact matches like exercise names and weights, merged with Reciprocal Rank Fusion.
3. Routes to the right agent via LangGraph — Session Coach, Nutrition, Progress Report, or Weekly Planner.
4. Streams the response back token by token.

The key architectural decision was hybrid retrieval. Dense search alone misses exact terms like "bench press 65kg" or "lat pulldown". BM25 alone misses semantic queries like "when did I feel tired after training". Both together — with RRF merging — handles both well.

---

## Stack

- **LangGraph** — multi-agent routing
- **Mistral AI** — LLM + intent classification + log extraction
- **Qdrant** — vector storage (runs locally)
- **BGE-base-en-v1.5** — embeddings
- **rank-bm25** — sparse retrieval
- **FastAPI** — streaming backend via SSE
- **React** — frontend

Everything except the Mistral API call runs locally. Your fitness data stays on your machine.

---

## Agents

**Session Coach** — takes your planned exercises, checks your history, gives progressive overload targets and warns about overtraining.

**Nutrition Agent** — logs meals from natural language, estimates macros using a built-in Indian food database, tracks your daily running total.

**Progress Agent** — weekly analysis of training consistency, nutrition averages, and what needs attention.

**Planner Agent** — builds a personalised weekly split based on your goal and which muscles have recovered.

---

## Project structure

```
fitmind/
├── agents/          # LangGraph agents + router
├── retrieval/       # Hybrid search (dense + BM25 + RRF)
├── ingestion/       # Log parsing, chunking, embedding, indexing
├── tools/           # Overload calculator, macro calculator, USDA API
├── memory/          # Auto-ingestion from chat
├── ui/
│   └── api.py       # FastAPI streaming backend
├── frontend/        # React UI
├── data/
│   ├── logs/        # Your personal workout logs
│   └── knowledge_base/
└── config/settings.py
```

---

## Running it locally

You need Python 3.10+, Node.js 18+, and a free Mistral API key from console.mistral.ai.

```bash
git clone https://github.com/prakyath231/fitmind-ai.git
cd fitmind-ai

python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux

pip install -r requirements.txt

cp .env.example .env
# add your MISTRAL_API_KEY to .env
```

Add your workout logs to `data/logs/daily_logs.txt` in this format:

```
Date: 2026-07-19
Type: Workout
Muscles Trained: Chest, Triceps

Exercises:
- Bench Press: 65kg, 4 sets x 10 reps
- Incline DB Press: 22kg, 3 sets x 12 reps

Nutrition:
- Breakfast: 4 eggs, toast
- Lunch: Chicken rice bowl

Estimated Macros:
- Calories: 1950
- Protein: 135g
- Carbs: 200g
- Fat: 48g

Notes: Felt strong. Bench improved from 60kg.

---
```

Then:

```bash
python ingest.py

# Terminal 1
uvicorn ui.api:app --reload --port 8000

# Terminal 2
cd frontend && npm install && npm start
```

Open http://localhost:3000.

---

## What's next

- Voice logging — speak your workout instead of typing
- Progress photos with vision model comparison
- Telegram bot for zero-friction daily check-ins
- Weekly coach report every Sunday
- Multi-user support

---

## About

Built by [Prakyath H N](https://github.com/prakyath231) — AI Engineer with 3 years of production GenAI experience, mostly in pharma and clinical trials. Built this because I needed it.