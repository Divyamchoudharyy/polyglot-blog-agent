from typing import Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()  # must run before the graph (and the LLM) is created

from src.blogagentic.graphs.graph_builder import graph  # noqa: E402

app = FastAPI(title="BlogAgentic")


class BlogRequest(BaseModel):
    topic: str
    language: Optional[str] = None


@app.post("/blogs")
def create_blogs(req: BlogRequest):
    topic = req.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="'topic' must not be empty")

    state_in = {"topic": topic}
    if req.language and req.language.strip():
        state_in["current_language"] = req.language.strip()

    try:
        state = graph.invoke(state_in)
    except Exception as e:  # LLM / network / quota errors
        raise HTTPException(status_code=502, detail=f"Blog generation failed: {e}")

    return {"data": state}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
