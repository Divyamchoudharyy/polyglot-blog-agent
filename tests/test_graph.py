import pytest
from fastapi.testclient import TestClient

from src.blogagentic.graphs.graph_builder import GraphBuilder


class Resp:
    def __init__(self, content):
        self.content = content


class FakeLLM:
    """Deterministic stand-in for ChatGroq (no network)."""

    def invoke(self, prompt):
        if "Translate" in prompt:
            lang = prompt.split(" into ")[1].split(".")[0]
            return Resp(f"[{lang}] translated")
        if "ONE creative" in prompt:
            return Resp('"# My Title"')
        return Resp("BODY")


@pytest.fixture
def graph():
    return GraphBuilder(FakeLLM()).setup_graph()


def test_topic_only_skips_translation(graph):
    out = graph.invoke({"topic": "AI"})
    assert out["blog"].title == "My Title"  # quotes and '#' stripped
    assert out["blog"].content == "BODY"


@pytest.mark.parametrize("lang", ["french", "French", "Spanish", "Tamil"])
def test_any_language_is_translated(graph, lang):
    out = graph.invoke({"topic": "AI", "current_language": lang})
    assert out["blog"].title == f"[{lang}] translated"
    assert out["blog"].content == f"[{lang}] translated"


@pytest.mark.parametrize("lang", ["", "   ", None])
def test_blank_language_means_no_translation(graph, lang):
    out = graph.invoke({"topic": "AI", "current_language": lang})
    assert out["blog"].content == "BODY"


def test_missing_topic_raises(graph):
    with pytest.raises(ValueError):
        graph.invoke({})


@pytest.fixture
def client(graph, monkeypatch):
    import app as appmod

    monkeypatch.setattr(appmod, "graph", graph)
    return TestClient(appmod.app)


def test_api_topic_and_language(client):
    r = client.post("/blogs", json={"topic": "AI", "language": "Spanish"})
    assert r.status_code == 200
    assert r.json()["data"]["blog"]["title"] == "[Spanish] translated"


def test_api_topic_only(client):
    r = client.post("/blogs", json={"topic": "AI"})
    assert r.status_code == 200
    assert r.json()["data"]["blog"]["content"] == "BODY"


def test_api_blank_topic_is_400(client):
    assert client.post("/blogs", json={"topic": "  "}).status_code == 400


def test_api_missing_topic_is_422(client):
    assert client.post("/blogs", json={}).status_code == 422


def test_api_llm_failure_is_502(client, monkeypatch):
    import app as appmod

    class Boom:
        def invoke(self, *a, **k):
            raise RuntimeError("groq down")

    monkeypatch.setattr(appmod, "graph", Boom())
    assert client.post("/blogs", json={"topic": "AI"}).status_code == 502
