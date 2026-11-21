"""
OPENAI MODEL — OpenAI API-based scoring.
==========================================
Uses GPT-4o-mini / GPT-4o to semantically evaluate promo candidates.

Setup:
  pip install openai
  Set OPENAI_API_KEY in config.py or as environment variable

Usage:
  Set MODEL = "openai" in config.py
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.base_model import BaseModel
import config


class OpenAIModel(BaseModel):
    """OpenAI API-based scoring model."""

    def __init__(self):
        super().__init__(name="openai")
        self.client = None
        self.model_name = config.OPENAI_MODEL_NAME
        self._init_client()

    def _init_client(self):
        try:
            from openai import OpenAI
        except ImportError:
            print("❌ openai not installed. Run: pip install openai")
            sys.exit(1)

        api_key = config.OPENAI_API_KEY or os.environ.get('OPENAI_API_KEY', '')
        if not api_key:
            print("❌ No OpenAI API key found.")
            print("   Set OPENAI_API_KEY in config.py or as environment variable.")
            sys.exit(1)

        self.client = OpenAI(api_key=api_key)
        print(f"   ✅ OpenAI model initialized: {self.model_name}")

    def score_promo_candidate(self, elements, window_start, window_end, episode_info):
        """Use OpenAI to score a promo candidate."""
        window_text = self.format_window_as_text(elements, window_start, window_end)
        duration = window_end - window_start

        prompt = f"""You are a social media editor for a microdrama app (like ReelShort/DramaBox).
Evaluate this {duration:.0f}-second clip from Episode {episode_info.get('episode_number', '?')}.

Episode logline: {episode_info.get('logline', 'N/A')}

CLIP CONTENT:
{window_text}

Score as a TikTok/Instagram promo (20-60s clip to attract new viewers).

Respond ONLY with valid JSON:
{{
  "hook": <0-15>,
  "emotion": <0-20>,
  "conflict": <0-15>,
  "cliffhanger": <0-10>,
  "standalone": <0-10>,
  "hook_text": "<first 3 seconds description>",
  "cliffhanger_text": "<ending moment description>",
  "why_it_works": "<one sentence>"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            text = response.choices[0].message.content.strip()
            if text.startswith('```'):
                text = text.split('\n', 1)[1]
                if text.endswith('```'):
                    text = text[:-3]
                text = text.strip()

            scores = json.loads(text)
            scores['hook'] = min(max(float(scores.get('hook', 0)), 0), 15)
            scores['emotion'] = min(max(float(scores.get('emotion', 0)), 0), 20)
            scores['conflict'] = min(max(float(scores.get('conflict', 0)), 0), 15)
            scores['cliffhanger'] = min(max(float(scores.get('cliffhanger', 0)), 0), 10)
            scores['standalone'] = min(max(float(scores.get('standalone', 0)), 0), 10)
            scores['total'] = round(sum([
                scores['hook'], scores['emotion'], scores['conflict'],
                scores['cliffhanger'], scores['standalone']
            ]), 2)
            return scores

        except Exception as e:
            print(f"      ⚠ OpenAI API error: {e}")
            return {
                'hook': 5, 'emotion': 5, 'conflict': 5,
                'cliffhanger': 5, 'standalone': 5, 'total': 25,
                'hook_text': 'API error', 'cliffhanger_text': 'API error',
                'why_it_works': 'API error'
            }

    def rank_promos(self, candidates, top_n=None):
        """Same ranking logic as Gemini model."""
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
