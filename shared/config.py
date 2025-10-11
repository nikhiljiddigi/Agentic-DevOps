import os
import dspy

def configure_lm():
    """Set up DSPy LM configuration."""
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise EnvironmentError("Please set OPENAI_API_KEY")
    lm = dspy.LM("openai/gpt-4o-mini", api_key=openai_key)
    dspy.configure(lm=lm)
