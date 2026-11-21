"""
STEP 1: SCREENPLAY PARSER
==========================
This script reads all 50 episode .txt files and converts them into
structured JSON data that our promo-finder can work with.

What it extracts from each episode:
  - Episode number & logline
  - Each scene with heading, location, start/end times
  - Each element (CAMERA, ACTION, DIALOGUE, SOUND FX) with:
      * Type, speaker, emotion/tone, start/end timestamps, content

Output: ../raw-outputs/parsed_episodes.json
"""

import os
import re
import json
import glob


def parse_timestamp(ts_str):
    """Convert 'MM:SS.FF' string to total seconds as float."""
    ts_str = ts_str.strip()
    match = re.match(r'(\d+):(\d+)\.(\d+)', ts_str)
    if match:
        minutes = int(match.group(1))
        seconds = int(match.group(2))
        fraction = int(match.group(3))
        return minutes * 60 + seconds + fraction / 100.0
    return 0.0


def parse_episode_file(filepath):
    """Parse a single episode .txt file into structured data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    episode = {
        'file': os.path.basename(filepath),
        'episode_number': None,
        'logline': '',
        'continuity_notes': '',
        'scenes': [],
        'all_elements': []  # flat list of every element across scenes
    }

    lines = content.split('\n')

    # --- Extract header info ---
    for line in lines:
        if line.startswith('EPISODE NUMBER:'):
            ep_text = line.replace('EPISODE NUMBER:', '').strip()
            # Extract just the number
            num_match = re.search(r'(\d+)', ep_text)
            episode['episode_number'] = int(num_match.group(1)) if num_match else ep_text
        elif line.startswith('EPISODE LOGLINE:'):
            episode['logline'] = line.replace('EPISODE LOGLINE:', '').strip()
        elif line.startswith('CONTINUITY NOTES:'):
            episode['continuity_notes'] = line.replace('CONTINUITY NOTES:', '').strip()

    # --- Split into scenes ---
    scene_blocks = re.split(r'(?=SCENE \d+)', content)

    for block in scene_blocks:
        block = block.strip()
        if not block.startswith('SCENE'):
            continue

        scene = {
            'scene_number': None,
            'heading': '',
            'location': '',
            'time_of_day': '',
            'start_time': 0.0,
            'end_time': 0.0,
            'elements': []
        }

        scene_lines = block.split('\n')

        # Parse scene header
        for line in scene_lines:
            line = line.strip()
            if re.match(r'SCENE \d+', line):
                num_match = re.search(r'SCENE (\d+)', line)
                scene['scene_number'] = int(num_match.group(1))
            elif line.startswith('Scene heading:'):
                heading = line.replace('Scene heading:', '').strip()
                scene['heading'] = heading
                # Extract location and time of day
                parts = heading.split('–')
                if len(parts) < 2:
                    parts = heading.split('-')
                scene['location'] = parts[0].replace('INT.', '').replace('EXT.', '').strip()
                scene['time_of_day'] = parts[-1].strip() if len(parts) > 1 else ''
            elif line.startswith('Scene start:'):
                scene['start_time'] = parse_timestamp(line.replace('Scene start:', '').strip())
            elif line.startswith('Scene end:'):
                scene['end_time'] = parse_timestamp(line.replace('Scene end:', '').strip())

        # --- Parse elements (CAMERA, ACTION, DIALOGUE, SOUND FX) ---
        # We use regex to find all **TYPE:** or **CHARACTER (Emotion):** blocks
        element_pattern = re.compile(
            r'\*\*(.+?):\*\*\s*\n'
            r'Start:\s*\(([^)]+)\)\s*\|\s*End:\s*\(([^)]+)\)\s*\n'
            r'(.*?)(?=\n\*\*|\n\nSCENE|\n--- SCRIPT END|\Z)',
            re.DOTALL
        )

        for match in element_pattern.finditer(block):
            header = match.group(1).strip()
            start_ts = match.group(2).strip()
            end_ts = match.group(3).strip()
            text = match.group(4).strip().strip('"')

            element = {
                'type': '',           # CAMERA, ACTION, DIALOGUE, SOUND_FX
                'speaker': '',        # Character name (for dialogue)
                'emotion': '',        # Emotional tone tag
                'start_time': parse_timestamp(start_ts),
                'end_time': parse_timestamp(end_ts),
                'start_ts_raw': start_ts,
                'end_ts_raw': end_ts,
                'text': text,
                'scene_number': scene['scene_number'],
                'episode_number': episode['episode_number']
            }

            # Classify the element type
            if header == 'CAMERA':
                element['type'] = 'CAMERA'
            elif header == 'ACTION':
                element['type'] = 'ACTION'
            elif header.startswith('SOUND FX') or header.startswith('SOUND'):
                element['type'] = 'SOUND_FX'
            else:
                # It's dialogue: parse speaker and emotion
                element['type'] = 'DIALOGUE'
                # Pattern: "CHARACTER_NAME (Emotion, Emotion)" or "CHARACTER_NAME (O.S.)"
                dial_match = re.match(r'(.+?)\s*\(([^)]*)\)', header)
                if dial_match:
                    element['speaker'] = dial_match.group(1).strip()
                    element['emotion'] = dial_match.group(2).strip()
                else:
                    element['speaker'] = header.strip()

            scene['elements'].append(element)
            episode['all_elements'].append(element)

        if scene['scene_number'] is not None:
            episode['scenes'].append(scene)

    return episode


def parse_all_episodes(input_dir):
    """Parse all episode files in the given directory."""
    pattern = os.path.join(input_dir, 'episode-*.txt')
    files = sorted(glob.glob(pattern))

    print(f"Found {len(files)} episode files in: {input_dir}")

    episodes = []
    for filepath in files:
        ep = parse_episode_file(filepath)
        episodes.append(ep)
        dialogue_count = sum(1 for e in ep['all_elements'] if e['type'] == 'DIALOGUE')
        print(f"  Parsed Episode {ep['episode_number']:>3}: "
              f"{len(ep['scenes'])} scenes, "
              f"{len(ep['all_elements'])} elements, "
              f"{dialogue_count} dialogue lines")

    return episodes


def main():
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    input_dir = os.path.join(os.path.dirname(project_dir),
                             'I Married a Broken Soldier. He was a Duke')
    output_dir = os.path.join(project_dir, 'raw-outputs')
    os.makedirs(output_dir, exist_ok=True)

    # Parse all episodes
    episodes = parse_all_episodes(input_dir)

    # Save to JSON
    output_path = os.path.join(output_dir, 'parsed_episodes.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(episodes, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Saved parsed data to: {output_path}")
    print(f"   Total episodes: {len(episodes)}")
    total_elements = sum(len(ep['all_elements']) for ep in episodes)
    total_dialogues = sum(1 for ep in episodes for e in ep['all_elements'] if e['type'] == 'DIALOGUE')
    print(f"   Total elements: {total_elements}")
    print(f"   Total dialogue lines: {total_dialogues}")

    return episodes


if __name__ == '__main__':
    main()
