"""
GEMINI MODEL — Google Gemini API-based scoring.
=================================================
Uses Gemini (free tier: gemini-2.0-flash) to semantically evaluate promo candidates.
Much better at understanding narrative tension, cliffhangers, and standalone clarity.

Setup:
  pip install google-generativeai
  Set GEMINI_API_KEY in config.py or as environment variable

Usage:
  Set MODEL = "gemini" in config.py
"""

import os
import sys
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.base_model import BaseModel
import config


class GeminiModel(BaseModel):
    """Gemini API-based scoring model for deeper promo understanding."""

    def __init__(self):
        super().__init__(name="gemini")
        self.client = None
        self.model_name = config.GEMINI_MODEL_NAME
        self._init_client()

    def _init_client(self):
        """Initialize the Gemini client."""
        try:
            import google.generativeai as genai
        except ImportError:
            print("❌ google-generativeai not installed.")
            print("   Run: pip install google-generativeai")
            print("   Or switch to MODEL = 'heuristic' in config.py")
            sys.exit(1)

        api_key = config.GEMINI_API_KEY or os.environ.get('GEMINI_API_KEY', '')
        if not api_key:
            print("❌ No Gemini API key found.")
            print("   Set GEMINI_API_KEY in config.py or as environment variable.")
            print("   Get a free key at: https://aistudio.google.com/apikey")
            sys.exit(1)

        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(self.model_name)
        print(f"   ✅ Gemini model initialized: {self.model_name}")

    def score_promo_candidate(self, elements, window_start, window_end, episode_info):
        """Use Gemini to semantically score a promo candidate."""
        # Format the window as readable text for the LLM
        window_text = self.format_window_as_text(elements, window_start, window_end)
        duration = window_end - window_start

        prompt = f"""You are a social media editor for a microdrama app (like ReelShort/DramaBox).
You're evaluating a {duration:.0f}-second clip from Episode {episode_info.get('episode_number', '?')}.

Episode logline: {episode_info.get('logline', 'N/A')}

CLIP CONTENT:
{window_text}

Score this clip as a potential PROMO for Instagram/TikTok (20-60 second clip to attract new viewers).

A good promo needs:
- HOOK (first 3 seconds): Something that makes a scrolling viewer STOP
- EMOTION: Intense feelings that make viewers care
- CONFLICT: Confrontation, drama, betrayal, action
- CLIFFHANGER: Ends on something UNRESOLVED so viewer needs to watch the show
- STANDALONE: Makes sense to someone who has NEVER seen the show

Respond ONLY with valid JSON (no markdown, no backticks):
{{
  "hook": <0-15 score>,
  "emotion": <0-20 score>,
  "conflict": <0-15 score>,
  "cliffhanger": <0-10 score>,
  "standalone": <0-10 score>,
  "hook_text": "<what happens in the first 3 seconds that grabs attention>",
  "cliffhanger_text": "<what the unresolved ending moment is>",
  "why_it_works": "<one sentence on why this works as a promo>"
}}"""

        try:
            response = self.client.generate_content(prompt)
            text = response.text.strip()
            # Clean potential markdown wrapping
            if text.startswith('```'):
                text = text.split('\n', 1)[1] if '\n' in text else text[3:]
                if text.endswith('```'):
                    text = text[:-3]
                text = text.strip()

            scores = json.loads(text)

            # Clamp scores to their max values
            scores['hook'] = min(max(float(scores.get('hook', 0)), 0), 15)
            scores['emotion'] = min(max(float(scores.get('emotion', 0)), 0), 20)
            scores['conflict'] = min(max(float(scores.get('conflict', 0)), 0), 15)
            scores['cliffhanger'] = min(max(float(scores.get('cliffhanger', 0)), 0), 10)
            scores['standalone'] = min(max(float(scores.get('standalone', 0)), 0), 10)
            scores['total'] = round(sum([
                scores['hook'], scores['emotion'], scores['conflict'],
                scores['cliffhanger'], scores['standalone']
            ]), 2)
            scores['hook_text'] = scores.get('hook_text', '')
            scores['cliffhanger_text'] = scores.get('cliffhanger_text', '')
            scores['why_it_works'] = scores.get('why_it_works', '')

            return scores

        except Exception as e:
            print(f"      ⚠ Gemini API error: {e}. Falling back to basic scores.")
            return {
                'hook': 5, 'emotion': 5, 'conflict': 5,
                'cliffhanger': 5, 'standalone': 5, 'total': 25,
                'hook_text': 'API error — could not evaluate',
                'cliffhanger_text': 'API error — could not evaluate',
                'why_it_works': 'Could not evaluate due to API error'
            }

    def rank_promos(self, candidates, top_n=None):
        """Rank promos using Gemini's scores with weighted formula."""
        if top_n is None:
            top_n = config.TOP_N_PROMOS

        for c in candidates:
            s = c['scores']
            weighted = (
                s['hook'] * config.WEIGHT_HOOK +
                s['emotion'] * config.WEIGHT_EMOTION +
                s['conflict'] * config.WEIGHT_CONFLICT +
                s['cliffhanger'] * config.WEIGHT_CLIFFHANGER +
                s['standalone'] * config.WEIGHT_STANDALONE
            )
            d = c['duration']
            if 30 <= d <= 45: weighted *= 1.10
            elif d < 20 or d > 55: weighted *= 0.90
            if c.get('dialogue_count', 0) >= 4: weighted *= 1.05
            c['rank_score'] = round(weighted, 3)
            c['why_it_works'] = s.get('why_it_works', '')

        candidates.sort(key=lambda c: c['rank_score'], reverse=True)

        # Diversify
        episode_counts = {}
        diversified = []
        for c in candidates:
            ep = c['episode_number']
            count = episode_counts.get(ep, 0)
            if count < config.MAX_PER_EPISODE:
                diversified.append(c)
                episode_counts[ep] = count + 1
            if len(diversified) >= top_n:
                break

        for i, promo in enumerate(diversified, 1):
            promo['rank'] = i

        return diversified
