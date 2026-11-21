"""
MODEL FACTORY — Loads the right model based on config.py settings.
"""

from models.base_model import BaseModel


def get_model(model_name=None):
    """
    Factory function that returns the appropriate model instance.

    Args:
        model_name: Override the model from config. Options:
                    "heuristic", "gemini", "openai", "hybrid"
                    If None, reads from config.MODEL

    Returns:
        An instance of BaseModel
    """
    import config

    name = model_name or config.MODEL

    if name == "heuristic":
        from models.heuristic_model import HeuristicModel
        return HeuristicModel()

    elif name == "gemini":
        from models.gemini_model import GeminiModel
        return GeminiModel()

    elif name == "openai":
        from models.openai_model import OpenAIModel
        return OpenAIModel()

    elif name == "hybrid":
        # Hybrid: use heuristic for fast pre-filter, then LLM for re-scoring top candidates
        # We return heuristic here; the main pipeline handles the hybrid logic
        from models.heuristic_model import HeuristicModel
        return HeuristicModel()

    else:
        raise ValueError(f"Unknown model: {name}. Use: heuristic, gemini, openai, hybrid")
