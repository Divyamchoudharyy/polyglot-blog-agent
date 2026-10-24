from src.blogagentic.states.blogState import Blog, BlogState


class BlogNode:
    """Nodes of the blog generation graph."""

    def __init__(self, llm):
        self.llm = llm

    def title_creation(self, state: BlogState):
        """Create the title for the blog."""
        topic = state.get("topic")
        if not topic:
            raise ValueError("'topic' is required to create a blog title")

        prompt = (
            "You are an expert blog content writer. "
            f"Generate ONE creative, SEO-friendly blog title for the topic: {topic}. "
            "Return only the title text - no options, no quotes, no markdown."
        )
        response = self.llm.invoke(prompt)
        title = response.content.strip().strip('"').lstrip("# ").strip()
        return {"blog": Blog(title=title, content="")}

    def content_generation(self, state: BlogState):
        """Generate the blog body for the topic and title."""
        topic = state["topic"]
        title = state["blog"].title

        prompt = (
            "You are an expert blog writer. Use Markdown formatting. "
            f"Write a detailed blog post with a clear breakdown of sections.\n"
            f"Topic: {topic}\nTitle: {title}\n"
            "Do not repeat the title as a heading."
        )
        response = self.llm.invoke(prompt)
        return {"blog": Blog(title=title, content=response.content)}

    def route_decision(self, state: BlogState):
        """Translate only if a language was requested, otherwise finish."""
        language = (state.get("current_language") or "").strip()
        return "translate" if language else "done"

    def translation(self, state: BlogState):
        """Translate the blog title and content to the requested language (any language)."""
        language = state["current_language"].strip()
        blog = state["blog"]

        def translate(text: str, what: str) -> str:
            prompt = (
                f"Translate the following blog {what} into {language}.\n"
                "- Maintain the original tone, style, and Markdown formatting.\n"
                "- Adapt cultural references and idioms appropriately.\n"
                f"- Return only the translated {what}, nothing else.\n\n"
                f"ORIGINAL {what.upper()}:\n{text}"
            )
            return self.llm.invoke(prompt).content.strip()

        return {
            "blog": Blog(
                title=translate(blog.title, "title"),
                content=translate(blog.content, "content"),
            )
        }
