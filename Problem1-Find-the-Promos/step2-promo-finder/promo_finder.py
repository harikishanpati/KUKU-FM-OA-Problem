"""
STEP 2: PROMO FINDER
====================
This script reads the parsed episode data (from Step 1) and uses
heuristic scoring to find the best promo-worthy moments.

HOW IT WORKS:
1. Slides a window (20-60 seconds) across each episode's timeline
2. Scores each window on 4 criteria:
   - HOOK SCORE: Does it start with something dramatic? (first 3 seconds)
   - EMOTION SCORE: How emotionally intense are the dialogues?
   - CONFLICT SCORE: Are there confrontations, betrayals, reveals?
   - CLIFFHANGER SCORE: Does it end on an unresolved moment?
3. Collects all candidate windows above a threshold
4. Removes overlapping candidates (keeps the highest scoring)

Output: ../raw-outputs/promo_candidates.json
"""

import os
import json
import re

# ==================== SCORING KEYWORDS ====================

# Words/phrases that make a HOOK (first 3 seconds) — stop-scrolling moments
HOOK_KEYWORDS = {
    'strong': [  # weight = 3
        'slap', 'punch', 'stab', 'kill', 'murder', 'poison', 'blood', 'scream',
        'dead', 'die', 'dying', 'shot', 'weapon', 'betray', 'affair', 'pregnant',
        'secret', 'arrest', 'caught', 'exposed', 'reveals', 'shocking'
    ],
    'medium': [  # weight = 2
        'furious', 'seething', 'outraged', 'horrified', 'terrified', 'shocked',
        'devastated', 'sobbing', 'crying', 'trembling', 'screaming', 'fierce',
        'dangerous', 'threatening', 'violent', 'cruel', 'wrenches', 'snatches',
        'shoves', 'grabs', 'crashes', 'breaks', 'confronts', 'accusing',
        'gasping', 'desperate', 'whisper'
    ],
    'mild': [  # weight = 1
        'angry', 'cold', 'stern', 'demanding', 'defiant', 'pleading', 'tears',
        'weeping', 'pain', 'hurt', 'wound', 'scar', 'dark', 'grim', 'tense'
    ]
}

# Emotion tags in dialogue that signal high drama
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

# Cliffhanger indicators — the promo should END on something unresolved
CLIFFHANGER_INDICATORS = [
    'cut to black', 'fade to black', 'screen fades', 'abrupt cut',
    'ominous', 'cliffhanger', 'unresolved', 'question', 'stares',
    'freezing in shock', 'eyes widen', 'horror', 'gasp', 'stumbling back',
    'walks away', 'turns away', 'silence', 'drone', 'swell'
]


def score_hook(elements, window_start, hook_window=3.0):
    """Score the first 3 seconds of a window — does it grab attention?"""
    score = 0
    hook_end = window_start + hook_window

    for elem in elements:
        if elem['start_time'] < hook_end and elem['end_time'] > window_start:
            text = (elem['text'] + ' ' + elem.get('emotion', '')).lower()

            for kw in HOOK_KEYWORDS['strong']:
                if kw in text:
                    score += 3
            for kw in HOOK_KEYWORDS['medium']:
                if kw in text:
                    score += 2
            for kw in HOOK_KEYWORDS['mild']:
                if kw in text:
                    score += 1

            # Dialogue with strong emotion in the opening = great hook
            if elem['type'] == 'DIALOGUE' and elem.get('emotion'):
                emotion_lower = elem['emotion'].lower()
                for emo in HIGH_DRAMA_EMOTIONS:
                    if emo in emotion_lower:
                        score += 3
                        break

    return min(score, 15)  # cap at 15


def score_emotion(elements, window_start, window_end):
    """Score overall emotional intensity of dialogue in the window."""
    score = 0
    dialogue_count = 0

    for elem in elements:
        if elem['start_time'] >= window_start and elem['end_time'] <= window_end:
            if elem['type'] == 'DIALOGUE':
                dialogue_count += 1
                emotion = elem.get('emotion', '').lower()

                for emo in HIGH_DRAMA_EMOTIONS:
                    if emo in emotion:
                        score += 3
                        break
                else:
                    for emo in MEDIUM_DRAMA_EMOTIONS:
                        if emo in emotion:
                            score += 2
                            break
                    else:
                        score += 0.5  # neutral dialogue still contributes a little

    # Bonus for having multiple dialogue exchanges (back-and-forth tension)
    if dialogue_count >= 4:
        score += 2
    if dialogue_count >= 6:
        score += 2

    return min(score, 20)  # cap at 20


def score_conflict(elements, window_start, window_end):
    """Score based on conflict words in ALL elements (camera, action, dialogue)."""
    score = 0
    conflict_words = [
        'betray', 'confront', 'accus', 'humiliat', 'insult', 'mock', 'cruel',
        'strike', 'hit', 'slap', 'shove', 'throw', 'wrench', 'snatch', 'grab',
        'fight', 'argue', 'scream', 'yell', 'shout', 'demand', 'threaten',
        'reveal', 'secret', 'lie', 'cheat', 'affair', 'poison', 'murder',
        'weapon', 'blood', 'wound', 'scar', 'arrest', 'prison', 'guilt',
        'refuse', 'reject', 'abandon', 'disown', 'disinherit', 'revoke',
        'banish', 'exile', 'dead', 'die', 'kill', 'exposed'
    ]

    for elem in elements:
        if elem['start_time'] >= window_start and elem['end_time'] <= window_end:
            text = elem['text'].lower()
            for word in conflict_words:
                if word in text:
                    score += 1.5

    return min(score, 15)  # cap at 15


def score_cliffhanger(elements, window_end, tail_window=5.0):
    """Score whether the window ends on an unresolved, cliffhanger-like moment."""
    score = 0
    tail_start = window_end - tail_window

    tail_elements = [e for e in elements
                     if e['start_time'] >= tail_start and e['end_time'] <= window_end + 1]

    for elem in tail_elements:
        text = (elem['text'] + ' ' + elem.get('emotion', '')).lower()

        for indicator in CLIFFHANGER_INDICATORS:
            if indicator in text:
                score += 2

        # A dialogue question at the end = great cliffhanger
        if elem['type'] == 'DIALOGUE' and elem['text'].strip().endswith('?'):
            score += 2

        # Strong emotion at the end
        if elem['type'] == 'DIALOGUE' and elem.get('emotion'):
            emotion = elem['emotion'].lower()
            for emo in HIGH_DRAMA_EMOTIONS:
                if emo in emotion:
                    score += 2
                    break

        # Sound FX often marks dramatic endings
        if elem['type'] == 'SOUND_FX':
            score += 1

    return min(score, 10)  # cap at 10


def score_standalone(elements, window_start, window_end):
    """Score how well the clip makes sense on its own (without prior context)."""
    score = 5  # start with a base score

    window_elements = [e for e in elements
                       if e['start_time'] >= window_start and e['end_time'] <= window_end]

    # Deduct if no dialogue (hard to understand without words)
    dialogue_count = sum(1 for e in window_elements if e['type'] == 'DIALOGUE')
    if dialogue_count == 0:
        score -= 3
    elif dialogue_count >= 2:
        score += 1

    # Bonus if the conflict is self-explanatory from dialogue
    dialogue_text = ' '.join(e['text'] for e in window_elements if e['type'] == 'DIALOGUE').lower()
    self_explanatory = ['you', 'i', 'my', 'your', 'why', 'how', 'what', 'who',
                        'husband', 'wife', 'father', 'mother', 'sister', 'brother',
                        'marry', 'love', 'hate', 'betray', 'leave', 'die']
    for word in self_explanatory:
        if word in dialogue_text:
            score += 0.3

    return min(max(score, 0), 10)  # clamp 0-10


def identify_hook_text(elements, window_start, hook_window=3.0):
    """Extract the actual hook moment text from the first 3 seconds."""
    hook_end = window_start + hook_window
    hook_parts = []

    for elem in elements:
        if elem['start_time'] < hook_end and elem['end_time'] > window_start:
            if elem['type'] == 'DIALOGUE':
                speaker = elem.get('speaker', 'Unknown')
                hook_parts.append(f'{speaker}: "{elem["text"]}"')
            elif elem['type'] in ('ACTION', 'CAMERA'):
                hook_parts.append(elem['text'][:100])

    return ' | '.join(hook_parts[:2]) if hook_parts else 'Visual hook from camera/action'


def identify_cliffhanger_text(elements, window_end, tail_window=5.0):
    """Extract the cliffhanger moment text from the last 5 seconds."""
    tail_start = window_end - tail_window
    cliff_parts = []

    tail_elements = [e for e in elements
                     if e['start_time'] >= tail_start and e['end_time'] <= window_end + 1]

    for elem in tail_elements[-3:]:  # last 3 elements
        if elem['type'] == 'DIALOGUE':
            speaker = elem.get('speaker', 'Unknown')
            cliff_parts.append(f'{speaker}: "{elem["text"]}"')
        elif elem['type'] in ('ACTION', 'CAMERA', 'SOUND_FX'):
            cliff_parts.append(elem['text'][:100])

    return ' | '.join(cliff_parts) if cliff_parts else 'Visual cliffhanger'


def find_promos_in_episode(episode, min_duration=20, max_duration=60, step=5):
    """
    Slide a window across the episode and score every candidate promo.

    Parameters:
        min_duration: Minimum promo length in seconds (20)
        max_duration: Maximum promo length in seconds (60)
        step: How many seconds to slide the window each time (5)
    """
    elements = episode['all_elements']
    if not elements:
        return []

    # Find the total timeline of this episode
    all_times = [e['end_time'] for e in elements]
    episode_end = max(all_times) if all_times else 0

    candidates = []

    # Try different window sizes
    for duration in range(min_duration, max_duration + 1, 10):
        # Slide the window across the episode
        window_start = 0.0
        while window_start + duration <= episode_end + 1:
            window_end = window_start + duration

            # Get elements in this window
            window_elements = [e for e in elements
                               if e['end_time'] > window_start and e['start_time'] < window_end]

            if len(window_elements) < 3:  # too few elements, skip
                window_start += step
                continue

            # Score this window
            hook_score = score_hook(elements, window_start)
            emotion_score = score_emotion(elements, window_start, window_end)
            conflict_score = score_conflict(elements, window_start, window_end)
            cliffhanger_score = score_cliffhanger(elements, window_end)
            standalone_score = score_standalone(elements, window_start, window_end)

            total_score = (hook_score + emotion_score + conflict_score +
                           cliffhanger_score + standalone_score)

            # Build the candidate
            candidate = {
                'episode_number': episode['episode_number'],
                'logline': episode['logline'],
                'start_time': round(window_start, 2),
                'end_time': round(window_end, 2),
                'duration': duration,
                'start_ts': f"{int(window_start // 60):02d}:{window_start % 60:05.2f}",
                'end_ts': f"{int(window_end // 60):02d}:{window_end % 60:05.2f}",
                'scores': {
                    'hook': round(hook_score, 2),
                    'emotion': round(emotion_score, 2),
                    'conflict': round(conflict_score, 2),
                    'cliffhanger': round(cliffhanger_score, 2),
                    'standalone': round(standalone_score, 2),
                    'total': round(total_score, 2)
                },
                'hook_text': identify_hook_text(elements, window_start),
                'cliffhanger_text': identify_cliffhanger_text(elements, window_end),
                'element_count': len(window_elements),
                'dialogue_count': sum(1 for e in window_elements if e['type'] == 'DIALOGUE')
            }

            candidates.append(candidate)
            window_start += step

    return candidates


def remove_overlaps(candidates, overlap_threshold=0.5):
    """Remove overlapping candidates, keeping the highest scoring ones."""
    if not candidates:
        return []

    # Sort by total score descending
    sorted_candidates = sorted(candidates, key=lambda c: c['scores']['total'], reverse=True)
    selected = []

    for candidate in sorted_candidates:
        # Check if this candidate overlaps too much with any already selected
        dominated = False
        for sel in selected:
            if sel['episode_number'] != candidate['episode_number']:
                continue

            # Calculate overlap
            overlap_start = max(candidate['start_time'], sel['start_time'])
            overlap_end = min(candidate['end_time'], sel['end_time'])
            overlap = max(0, overlap_end - overlap_start)

            shorter_duration = min(candidate['duration'], sel['duration'])
            if shorter_duration > 0 and overlap / shorter_duration > overlap_threshold:
                dominated = True
                break

        if not dominated:
            selected.append(candidate)

    return selected


def find_all_promos(episodes):
    """Find promos across all episodes."""
    all_candidates = []

    for episode in episodes:
        candidates = find_promos_in_episode(episode)
        # Keep only the non-overlapping best candidates per episode
        best = remove_overlaps(candidates)
        all_candidates.extend(best)

        if best:
            top = best[0]
            print(f"  Episode {episode['episode_number']:>3}: "
                  f"Found {len(candidates)} candidates → {len(best)} non-overlapping | "
                  f"Best score: {top['scores']['total']:.1f}")
        else:
            print(f"  Episode {episode['episode_number']:>3}: No strong promo candidates found")

    return all_candidates


def main():
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    input_path = os.path.join(project_dir, 'raw-outputs', 'parsed_episodes.json')
    output_path = os.path.join(project_dir, 'raw-outputs', 'promo_candidates.json')

    # Load parsed episodes
    print("Loading parsed episodes...")
    with open(input_path, 'r', encoding='utf-8') as f:
        episodes = json.load(f)
    print(f"Loaded {len(episodes)} episodes.\n")

    # Find promos
    print("Finding promo candidates...")
    candidates = find_all_promos(episodes)

    # Save
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(candidates, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Found {len(candidates)} promo candidates total")
    print(f"   Saved to: {output_path}")

    return candidates


if __name__ == '__main__':
    main()
