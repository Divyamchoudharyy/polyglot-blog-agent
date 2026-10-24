import os

# graph_builder creates the Groq client at import time, so a key must exist.
os.environ.setdefault("GROQ_API_KEY", "test-key")
