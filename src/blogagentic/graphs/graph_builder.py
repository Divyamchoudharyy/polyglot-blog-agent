from langgraph.graph import END, START, StateGraph

from src.blogagentic.llms.groq_llm import GroqLLM
from src.blogagentic.nodes.blog_node import BlogNode
from src.blogagentic.states.blogState import BlogState


class GraphBuilder:
    def __init__(self, llm):
        self.llm = llm

    def setup_graph(self):
        """START -> title -> content -> (translation if language given) -> END"""
        builder = StateGraph(BlogState)
        nodes = BlogNode(self.llm)

        builder.add_node("title_creation", nodes.title_creation)
        builder.add_node("content_generation", nodes.content_generation)
        builder.add_node("translation", nodes.translation)

        builder.add_edge(START, "title_creation")
        builder.add_edge("title_creation", "content_generation")
        builder.add_conditional_edges(
            "content_generation",
            nodes.route_decision,
            {"translate": "translation", "done": END},
        )
        builder.add_edge("translation", END)

        return builder.compile()


# Compiled graph exported for `langgraph dev` (see langgraph.json).
# Input: {"topic": "..."} or {"topic": "...", "current_language": "Spanish"}
graph = GraphBuilder(GroqLLM().get_llm()).setup_graph()
