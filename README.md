# BlogAgentic

LangGraph + Groq blog generator: `START -> title -> content -> (translation) -> END`.
Translation runs only when a language is given, and works for any language.

## Setup
    cp .env.example .env      # then put your real keys in .env
    uv sync                   # or: pip install -r requirements.txt

## Run
    python app.py             # API on :8000  (POST /blogs)
    langgraph dev             # LangGraph Studio

## Request
    curl -X POST localhost:8000/blogs -H "Content-Type: application/json" -d @request.json
    curl -X POST localhost:8000/blogs -H "Content-Type: application/json" -d @request_language.json
