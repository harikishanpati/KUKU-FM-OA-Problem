"""
HEURISTIC MODEL — Fast keyword-based scoring (no API needed).
==============================================================
This is the default model. It uses keyword matching and emotion tag analysis
to score promo candidates. Fast, free, deterministic.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.base_model import BaseModel
import config


# ==================== SCORING KEYWORDS ====================

HOOK_KEYWORDS = {
    'strong': [
        'slap', 'punch', 'stab', 'kill', 'murder', 'poison', 'blood', 'scream',
        'dead', 'die', 'dying', 'shot', 'weapon', 'betray', 'affair', 'pregnant',
        'secret', 'arrest', 'caught', 'exposed', 'reveals', 'shocking'
    ],
    'medium': [
        'furious', 'seething', 'outraged', 'horrified', 'terrified', 'shocked',
        'devastated', 'sobbing', 'crying', 'trembling', 'screaming', 'fierce',
        'dangerous', 'threatening', 'violent', 'cruel', 'wrenches', 'snatches',
        'shoves', 'grabs', 'crashes', 'breaks', 'confronts', 'accusing',
        'gasping', 'desperate', 'whisper'
    ],
    'mild': [
        'angry', 'cold', 'stern', 'demanding', 'defiant', 'pleading', 'tears',
        'weeping', 'pain', 'hurt', 'wound', 'scar', 'dark', 'grim', 'tense'
    ]
}

HIGH_DRAMA_EMOTIONS = [
    'seething', 'furious', 'outraged', 'horrified', 'terrified', 'shocked',
    'devastated', 'screaming', 'desperate', 'betrayed', 'dangerous', 'fierce',
    'venomous', 'cruel', 'mocking', 'gloating', 'threatening', 'lethal',
    'volatile', 'choking', 'broken', 'anguished', 'tormented', 'piercing',
    'incredulous', 'alarmed', 'chilling', 'carnal', 'seductive'
]

MEDIUM_DRAMA_EMOTIONS = [
    'cold', 'stern', 'demanding', 'defiant', 'pleading', 'trembling',
    'shaking', 'crying', 'accusing', 'painful', 'raw', 'blunt', 'sharp',
    'suspicious', 'anxious', 'fearful', 'grim', 'calculating', 'scornful',
    'arrogant', 'dismissive', 'disgusted', 'condemnatory', 'reproachful'
]

CONFLICT_WORDS = [
    'betray', 'confront', 'accus', 'humiliat', 'insult', 'mock', 'cruel',
    'strike', 'hit', 'slap', 'shove', 'throw', 'wrench', 'snatch', 'grab',
    'fight', 'argue', 'scream', 'yell', 'shout', 'demand', 'threaten',
    'reveal', 'secret', 'lie', 'cheat', 'affair', 'poison', 'murder',
    'weapon', 'blood', 'wound', 'scar', 'arrest', 'prison', 'guilt',
    'refuse', 'reject', 'abandon', 'disown', 'disinherit', 'revoke',
    'banish', 'exile', 'dead', 'die', 'kill', 'exposed'
]

CLIFFHANGER_INDICATORS = [
    'cut to black', 'fade to black', 'screen fades', 'abrupt cut',
    'ominous', 'cliffhanger', 'unresolved', 'question', 'stares',
    'freezing in shock', 'eyes widen', 'horror', 'gasp', 'stumbling back',
    'walks away', 'turns away', 'silence', 'drone', 'swell'
]


class HeuristicModel(BaseModel):
    """Fast keyword-based scoring model. No API needed."""

    def __init__(self):
        super().__init__(name="heuristic")

    def _score_hook(self, elements, window_start):
        score = 0
        hook_end = window_start + config.HOOK_WINDOW_SECONDS
        for elem in elements:
            if elem['start_time'] < hook_end and elem['end_time'] > window_start:
                text = (elem['text'] + ' ' + elem.get('emotion', '')).lower()
                for kw in HOOK_KEYWORDS['strong']:
                    if kw in text: score += 3
                for kw in HOOK_KEYWORDS['medium']:
                    if kw in text: score += 2
                for kw in HOOK_KEYWORDS['mild']:
                    if kw in text: score += 1
                if elem['type'] == 'DIALOGUE' and elem.get('emotion'):
                    for emo in HIGH_DRAMA_EMOTIONS:
                        if emo in elem['emotion'].lower():
                            score += 3
                            break
        return min(score, 15)

    def _score_emotion(self, elements, window_start, window_end):
        score = 0
        dialogue_count = 0
        for elem in elements:
            if elem['start_time'] >= window_start and elem['end_time'] <= window_end:
                if elem['type'] == 'DIALOGUE':
                    dialogue_count += 1
                    emotion = elem.get('emotion', '').lower()
                    matched = False
                    for emo in HIGH_DRAMA_EMOTIONS:
                        if emo in emotion:
                            score += 3
                            matched = True
                            break
                    if not matched:
                        for emo in MEDIUM_DRAMA_EMOTIONS:
                            if emo in emotion:
                                score += 2
                                matched = True
                                break
                    if not matched:
                        score += 0.5
        if dialogue_count >= 4: score += 2
        if dialogue_count >= 6: score += 2
        return min(score, 20)

    def _score_conflict(self, elements, window_start, window_end):
        score = 0
        for elem in elements:
            if elem['start_time'] >= window_start and elem['end_time'] <= window_end:
                text = elem['text'].lower()
                for word in CONFLICT_WORDS:
                    if word in text: score += 1.5
        return min(score, 15)

    def _score_cliffhanger(self, elements, window_end):
        score = 0
        tail_start = window_end - config.CLIFFHANGER_TAIL_SECONDS
        tail_elements = [e for e in elements
                         if e['start_time'] >= tail_start and e['end_time'] <= window_end + 1]
        for elem in tail_elements:
            text = (elem['text'] + ' ' + elem.get('emotion', '')).lower()
            for indicator in CLIFFHANGER_INDICATORS:
                if indicator in text: score += 2
            if elem['type'] == 'DIALOGUE' and elem['text'].strip().endswith('?'):
                score += 2
            if elem['type'] == 'DIALOGUE' and elem.get('emotion'):
                for emo in HIGH_DRAMA_EMOTIONS:
                    if emo in elem['emotion'].lower():
                        score += 2
                        break
            if elem['type'] == 'SOUND_FX':
                score += 1
        return min(score, 10)

    def _score_standalone(self, elements, window_start, window_end):
        score = 5
        window_elements = self.get_elements_in_window(elements, window_start, window_end)
        dialogue_count = sum(1 for e in window_elements if e['type'] == 'DIALOGUE')
        if dialogue_count == 0: score -= 3
        elif dialogue_count >= 2: score += 1
        dialogue_text = ' '.join(e['text'] for e in window_elements if e['type'] == 'DIALOGUE').lower()
        for word in ['you', 'i', 'my', 'your', 'why', 'how', 'what', 'who',
                      'husband', 'wife', 'father', 'mother', 'sister', 'brother',
                      'marry', 'love', 'hate', 'betray', 'leave', 'die']:
            if word in dialogue_text: score += 0.3
        return min(max(score, 0), 10)

    def _identify_hook_text(self, elements, window_start):
        hook_end = window_start + config.HOOK_WINDOW_SECONDS
        parts = []
        for elem in elements:
            if elem['start_time'] < hook_end and elem['end_time'] > window_start:
                if elem['type'] == 'DIALOGUE':
                    parts.append(f'{elem.get("speaker","?")}: "{elem["text"]}"')
                elif elem['type'] in ('ACTION', 'CAMERA'):
                    parts.append(elem['text'][:100])
        return ' | '.join(parts[:2]) if parts else 'Visual hook from camera/action'

    def _identify_cliffhanger_text(self, elements, window_end):
        tail_start = window_end - config.CLIFFHANGER_TAIL_SECONDS
        tail_elements = [e for e in elements
                         if e['start_time'] >= tail_start and e['end_time'] <= window_end + 1]
        parts = []
        for elem in tail_elements[-3:]:
            if elem['type'] == 'DIALOGUE':
                parts.append(f'{elem.get("speaker","?")}: "{elem["text"]}"')
            elif elem['type'] in ('ACTION', 'CAMERA', 'SOUND_FX'):
                parts.append(elem['text'][:100])
        return ' | '.join(parts) if parts else 'Visual cliffhanger'

    def score_promo_candidate(self, elements, window_start, window_end, episode_info):
        hook = self._score_hook(elements, window_start)
        emotion = self._score_emotion(elements, window_start, window_end)
        conflict = self._score_conflict(elements, window_start, window_end)
        cliffhanger = self._score_cliffhanger(elements, window_end)
        standalone = self._score_standalone(elements, window_start, window_end)
        total = hook + emotion + conflict + cliffhanger + standalone

        return {
            'hook': round(hook, 2),
            'emotion': round(emotion, 2),
            'conflict': round(conflict, 2),
            'cliffhanger': round(cliffhanger, 2),
            'standalone': round(standalone, 2),
            'total': round(total, 2),
            'hook_text': self._identify_hook_text(elements, window_start),
            'cliffhanger_text': self._identify_cliffhanger_text(elements, window_end),
            'why_it_works': ''  # filled by ranker
        }

    def rank_promos(self, candidates, top_n=None):
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

            # Generate why_it_works
            reasons = []
            if s['hook'] >= 6: reasons.append("Strong opening hook that stops scrollers")
            elif s['hook'] >= 3: reasons.append("Decent attention-grabbing opening")
            if s['emotion'] >= 10: reasons.append("Extremely high emotional intensity")
            elif s['emotion'] >= 6: reasons.append("Strong emotional dialogue")
            if s['conflict'] >= 8: reasons.append("Intense conflict/confrontation")
            elif s['conflict'] >= 4: reasons.append("Clear dramatic tension")
            if s['cliffhanger'] >= 6: reasons.append("Powerful cliffhanger ending")
            elif s['cliffhanger'] >= 3: reasons.append("Leaves viewer wanting more")
            if s['standalone'] >= 7: reasons.append("Self-explanatory to new viewers")
            c['scores']['why_it_works'] = "; ".join(reasons) if reasons else "Moderate dramatic content"
            c['why_it_works'] = c['scores']['why_it_works']

        candidates.sort(key=lambda c: c['rank_score'], reverse=True)

        # Diversify across episodes
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
