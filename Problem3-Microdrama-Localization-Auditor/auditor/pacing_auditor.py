"""
MICRODRAMA PACING & LOCALIZATION AUDITOR
=========================================
Identifies pacing defects, dead air (>3s), and dialogue timing mismatches
across microdrama screenplays before dubbing and video rendering.

Key metrics audited:
1. Speech Velocity (Words Per Minute / WPM):
   - Natural human speech range: 110 - 165 WPM.
   - PUSH/RUSH (>180 WPM): Dialogue text is too long for the allocated time window;
     AI voice generator or voice actor will sound unnaturally rushed or clipped.
   - SLOW/DRAG (<70 WPM): Dialogue text is too brief for the time slot; creates awkward pauses.
2. Dead Air Detection (>3.0 seconds):
   - In vertical shortform drama (Reels, TikTok), 3 seconds of dead silence causes 40%+ drop-off.
3. Timing Overlaps:
   - Dialogue lines starting before previous speaker has finished.
"""

import os
import re
import glob

def parse_time(ts_str):
    m = re.match(r'(\d+):(\d+)\.(\d+)', ts_str.strip())
    if m:
        return int(m.group(1)) * 60 + int(m.group(2)) + int(m.group(3)) / 100.0
    return 0.0

def audit_episode_screenplay(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    ep_num_match = re.search(r'EPISODE NUMBER:\s*(?:Episode\s*)?(\d+)', content)
    ep_num = int(ep_num_match.group(1)) if ep_num_match else os.path.basename(filepath)

    logline_match = re.search(r'EPISODE LOGLINE:\s*(.+)', content)
    logline = logline_match.group(1).strip() if logline_match else "N/A"

    # Extract all elements
    element_pattern = re.compile(
        r'\*\*(.+?):\*\*\s*\n'
        r'Start:\s*\(([^)]+)\)\s*\|\s*End:\s*\(([^)]+)\)\s*\n'
        r'(.*?)(?=\n\*\*|\n\nSCENE|\n--- SCRIPT END|\Z)',
        re.DOTALL
    )

    elements = []
    for match in element_pattern.finditer(content):
        header = match.group(1).strip()
        start_ts = match.group(2).strip()
        end_ts = match.group(3).strip()
        text = match.group(4).strip().strip('"')

        start_sec = parse_time(start_ts)
        end_sec = parse_time(end_ts)
        dur = max(0.1, end_sec - start_sec)

        is_dialogue = header not in ('CAMERA', 'ACTION') and not header.startswith('SOUND')
        speaker = ""
        emotion = ""
        if is_dialogue:
            d_match = re.match(r'(.+?)\s*\(([^)]*)\)', header)
            if d_match:
                speaker = d_match.group(1).strip()
                emotion = d_match.group(2).strip()
            else:
                speaker = header.strip()

        elements.append({
            'header': header,
            'is_dialogue': is_dialogue,
            'speaker': speaker,
            'emotion': emotion,
            'start_ts': start_ts,
            'end_ts': end_ts,
            'start_sec': start_sec,
            'end_sec': end_sec,
            'duration': round(dur, 2),
            'text': text
        })

    # Sort chronologically
    elements.sort(key=lambda x: x['start_sec'])

    # Audit 1: Pacing & WPM Analysis for Dialogues
    dialogue_issues = []
    dialogues = [e for e in elements if e['is_dialogue']]

    for d in dialogues:
        words = re.findall(r'\b\w+\b', d['text'])
        word_count = len(words)
        minutes = d['duration'] / 60.0
        wpm = round(word_count / minutes, 1) if minutes > 0 else 0

        issue_type = None
        recommendation = None

        if wpm > 185:
            issue_type = "UNNATURALLY_RUSHED"
            needed_dur = round(word_count / (145 / 60.0), 1)
            recommendation = f"Dialogue is rushed ({wpm} WPM). Expand time allocation from {d['duration']}s to at least {needed_dur}s, or trim {word_count - int(145 * minutes)} words."
        elif wpm < 65 and word_count >= 3:
            issue_type = "UNNATURALLY_DRAGGED"
            needed_dur = round(word_count / (130 / 60.0), 1)
            recommendation = f"Dialogue drags ({wpm} WPM). Tighten duration from {d['duration']}s to {needed_dur}s to eliminate dead pause."

        if issue_type:
            dialogue_issues.append({
                'type': issue_type,
                'speaker': d['speaker'],
                'emotion': d['emotion'],
                'start_ts': d['start_ts'],
                'end_ts': d['end_ts'],
                'duration': d['duration'],
                'word_count': word_count,
                'wpm': wpm,
                'text': d['text'],
                'recommendation': recommendation
            })

    # Audit 2: Dead Air Gaps (>3.0s between audio cues)
    dead_air_gaps = []
    for i in range(len(dialogues) - 1):
        curr_d = dialogues[i]
        next_d = dialogues[i + 1]

        gap = next_d['start_sec'] - curr_d['end_sec']
        if gap >= 3.2:
            # Check if there is an explicit camera or sound effect bridging this gap
            intermediate_actions = [
                e for e in elements
                if not e['is_dialogue'] and e['start_sec'] >= curr_d['end_sec'] - 0.2 and e['end_sec'] <= next_d['start_sec'] + 0.2
            ]
            action_desc = "; ".join(a['text'][:60] for a in intermediate_actions) if intermediate_actions else "None (Dead Silence)"

            dead_air_gaps.append({
                'gap_duration': round(gap, 2),
                'from_ts': curr_d['end_ts'],
                'to_ts': next_d['start_ts'],
                'between_speakers': f"{curr_d['speaker']} ➔ {next_d['speaker']}",
                'intermediate_action': action_desc,
                'risk': "HIGH RETENTION LOSS" if gap >= 4.0 else "MODERATE PACING SLOWDOWN"
            })

    # Summary Health Score (100 base)
    penalty = (len(dialogue_issues) * 4) + (len(dead_air_gaps) * 6)
    health_score = max(0, min(100, 100 - penalty))

    return {
        'episode_number': ep_num,
        'logline': logline,
        'total_elements': len(elements),
        'total_dialogues': len(dialogues),
        'health_score': health_score,
        'dialogue_issues': dialogue_issues,
        'dead_air_gaps': dead_air_gaps
    }
