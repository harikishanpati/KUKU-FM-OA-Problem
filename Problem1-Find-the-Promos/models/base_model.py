"""
MODEL INTERFACE — Base class that all scoring models implement.
================================================================
To add a new model (Claude, Llama, Mistral, etc.):
  1. Create a new file in models/ (e.g., claude_model.py)
  2. Subclass BaseModel
  3. Implement score_promo_candidate() and rank_promos()
  4. Add it to models/__init__.py
  5. Set MODEL = "claude" in config.py

That's it. The rest of the pipeline stays the same.
"""

from abc import ABC, abstractmethod


class BaseModel(ABC):
    """
    Abstract base class for promo scoring models.

    Every model must implement two methods:
      - score_promo_candidate(): Score a single promo window
      - rank_promos(): Take scored candidates and produce a ranked list
    """

    def __init__(self, name="base"):
        self.name = name

    @abstractmethod
    def score_promo_candidate(self, elements, window_start, window_end, episode_info):
        """
        Score a single promo candidate window.

        Args:
            elements: List of parsed elements (dialogue, camera, action, sound_fx)
                      Each element has: type, speaker, emotion, start_time, end_time, text
            window_start: Start time in seconds
            window_end: End time in seconds
            episode_info: Dict with episode_number, logline, continuity_notes

        Returns:
            dict with scores:
                {
                    'hook': float,         # 0-15: Does it grab attention in first 3s?
                    'emotion': float,      # 0-20: How emotionally intense?
                    'conflict': float,     # 0-15: Is there confrontation/drama?
                    'cliffhanger': float,  # 0-10: Does it end unresolved?
                    'standalone': float,   # 0-10: Makes sense without context?
                    'total': float,        # Sum of all scores
                    'hook_text': str,      # Description of the hook moment
                    'cliffhanger_text': str,  # Description of the ending
                    'why_it_works': str    # One-line explanation
                }
        """
        pass

    @abstractmethod
    def rank_promos(self, candidates, top_n=20):
        """
        Take a list of scored candidates and produce a final ranked list.

        Args:
            candidates: List of candidate dicts (each with 'scores' from score_promo_candidate)
            top_n: How many to return

        Returns:
            List of top_n candidates, ranked best-first, with 'rank' and 'rank_score' added
        """
        pass

    def get_elements_in_window(self, elements, start, end):
        """Helper: Get elements that fall within a time window."""
        return [e for e in elements
                if e['end_time'] > start and e['start_time'] < end]

    def get_dialogue_in_window(self, elements, start, end):
        """Helper: Get only dialogue elements within a time window."""
        return [e for e in elements
                if e['type'] == 'DIALOGUE' and e['end_time'] > start and e['start_time'] < end]

    def format_window_as_text(self, elements, start, end):
        """
        Helper: Format a time window's elements as readable text.
        Useful for sending to an LLM.
        """
        window_elements = self.get_elements_in_window(elements, start, end)
        lines = []
        for elem in window_elements:
            ts = f"[{elem['start_time']:.1f}s-{elem['end_time']:.1f}s]"
            if elem['type'] == 'DIALOGUE':
                speaker = elem.get('speaker', 'Unknown')
                emotion = f" ({elem['emotion']})" if elem.get('emotion') else ''
                lines.append(f"{ts} {speaker}{emotion}: \"{elem['text']}\"")
            elif elem['type'] == 'ACTION':
                lines.append(f"{ts} ACTION: {elem['text']}")
            elif elem['type'] == 'CAMERA':
                lines.append(f"{ts} CAMERA: {elem['text']}")
            elif elem['type'] == 'SOUND_FX':
                lines.append(f"{ts} SOUND: {elem['text']}")
        return '\n'.join(lines)
