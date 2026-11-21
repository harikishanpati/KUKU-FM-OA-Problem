"""
MAIN RUNNER — Problem 1: Find the Promos
=========================================
Fully re-runnable on any input, with swappable models.

Usage:
    # Default: use the input pack with heuristic model
    python main.py

    # Run on a NEW show (interview scenario):
    python main.py --input "path/to/new-show-scripts/"

    # Switch to Gemini model:
    python main.py --model gemini

    # Switch to OpenAI model:
    python main.py --model openai

    # Hybrid: heuristic pre-filter + LLM re-rank:
    python main.py --model hybrid

    # Custom output folder:
    python main.py --input "path/to/scripts" --output "path/to/results"

    # Change top N promos:
    python main.py --top 30

All settings can also be changed in config.py
"""

import sys
import os
import time
import json
import argparse

# Ensure this script's directory is in the path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'step1-parser'))
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'step2-promo-finder'))
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'step3-ranker'))
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'step4-quality-check'))

import config


def parse_args():
    parser = argparse.ArgumentParser(
        description="Find the best promos in microdrama screenplays.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                    # Run with defaults
  python main.py --input "../New Show Scripts/"      # New show
  python main.py --model gemini                      # Use Gemini API
  python main.py --model hybrid --top 30             # Hybrid + more promos
        """
    )
    parser.add_argument(
        '--input', '-i',
        help='Path to folder containing episode-*.txt screenplay files. '
             'Defaults to the input pack folder next to this project.',
        default=None
    )
    parser.add_argument(
        '--output', '-o',
        help='Path to output folder. Defaults to raw-outputs/ in this project.',
        default=None
    )
    parser.add_argument(
        '--model', '-m',
        choices=['heuristic', 'gemini', 'openai', 'hybrid'],
        help='Scoring model to use (default: from config.py)',
        default=None
    )
    parser.add_argument(
        '--top', '-n',
        type=int,
        help=f'Number of top promos to output (default: {config.TOP_N_PROMOS})',
        default=None
    )
    parser.add_argument(
        '--api-key',
        help='API key for the selected model (alternative to config.py / env var)',
        default=None
    )
    return parser.parse_args()


def resolve_input_dir(user_input):
    """Find the screenplay folder. Smart defaults for the assignment input pack."""
    if user_input:
        path = os.path.abspath(user_input)
        if os.path.isdir(path):
            return path
        else:
            print(f"❌ Input directory not found: {path}")
            sys.exit(1)

    # Default: look for the input pack relative to this project
    parent = os.path.dirname(SCRIPT_DIR)
    candidates = [
        os.path.join(parent, 'I Married a Broken Soldier. He was a Duke'),
    ]
    # Also check if screenplay files are directly in parent
    import glob
    if glob.glob(os.path.join(parent, 'episode-*.txt')):
        candidates.insert(0, parent)

    for path in candidates:
        if os.path.isdir(path):
            return path

    print("❌ Could not find screenplay files.")
    print("   Use --input to specify the folder containing episode-*.txt files.")
    print(f"   Looked in: {candidates}")
    sys.exit(1)


def run_pipeline(input_dir, output_dir, model_name, top_n, api_key):
    """Run the full promo-finding pipeline."""
    start = time.time()

    # --- Apply overrides to config ---
    if model_name:
        config.MODEL = model_name
    if top_n:
        config.TOP_N_PROMOS = top_n
    if api_key:
        if config.MODEL == 'gemini':
            config.GEMINI_API_KEY = api_key
        elif config.MODEL == 'openai':
            config.OPENAI_API_KEY = api_key

    os.makedirs(output_dir, exist_ok=True)

    # Detect show name from folder
    show_name = os.path.basename(input_dir)

    print("=" * 70)
    print(f"  FIND THE PROMOS — Full Pipeline")
    print(f"  Show: {show_name}")
    print(f"  Model: {config.MODEL}")
    print(f"  Input: {input_dir}")
    print(f"  Output: {output_dir}")
    print("=" * 70)

    # ─── STEP 1: PARSE ────────────────────────────────────────────
    print(f"\n{'▶ ' * 3}STEP 1: PARSING SCREENPLAYS{'◀ ' * 3}")
    print("-" * 50)

    from screenplay_parser import parse_all_episodes
    episodes = parse_all_episodes(input_dir)

    parsed_path = os.path.join(output_dir, 'parsed_episodes.json')
    with open(parsed_path, 'w', encoding='utf-8') as f:
        json.dump(episodes, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved: {parsed_path}")

    # ─── STEP 2: FIND PROMO CANDIDATES ────────────────────────────
    print(f"\n{'▶ ' * 3}STEP 2: FINDING PROMO CANDIDATES{'◀ ' * 3}")
    print("-" * 50)

    from models import get_model
    model = get_model(config.MODEL if config.MODEL != 'hybrid' else 'heuristic')
    print(f"   Using model: {model.name}")

    all_candidates = []
    for episode in episodes:
        elements = episode['all_elements']
        if not elements:
            continue

        episode_end = max(e['end_time'] for e in elements)
        episode_info = {
            'episode_number': episode['episode_number'],
            'logline': episode['logline'],
            'continuity_notes': episode.get('continuity_notes', '')
        }

        ep_candidates = []
        for duration in config.WINDOW_SIZES:
            window_start = 0.0
            while window_start + duration <= episode_end + 1:
                window_end = window_start + duration

                window_elements = model.get_elements_in_window(
                    elements, window_start, window_end)

                if len(window_elements) >= 3:
                    scores = model.score_promo_candidate(
                        elements, window_start, window_end, episode_info)

                    candidate = {
                        'episode_number': episode['episode_number'],
                        'logline': episode['logline'],
                        'start_time': round(window_start, 2),
                        'end_time': round(window_end, 2),
                        'duration': duration,
                        'start_ts': f"{int(window_start // 60):02d}:{window_start % 60:05.2f}",
                        'end_ts': f"{int(window_end // 60):02d}:{window_end % 60:05.2f}",
                        'scores': scores,
                        'hook_text': scores.get('hook_text', ''),
                        'cliffhanger_text': scores.get('cliffhanger_text', ''),
                        'element_count': len(window_elements),
                        'dialogue_count': sum(1 for e in window_elements
                                              if e['type'] == 'DIALOGUE')
                    }
                    ep_candidates.append(candidate)

                window_start += config.WINDOW_STEP

        # Remove overlaps within this episode
        ep_candidates.sort(key=lambda c: c['scores']['total'], reverse=True)
        selected = []
        for cand in ep_candidates:
            overlap = False
            for sel in selected:
                o_start = max(cand['start_time'], sel['start_time'])
                o_end = min(cand['end_time'], sel['end_time'])
                o_len = max(0, o_end - o_start)
                shorter = min(cand['duration'], sel['duration'])
                if shorter > 0 and o_len / shorter > config.OVERLAP_THRESHOLD:
                    overlap = True
                    break
            if not overlap:
                selected.append(cand)

        all_candidates.extend(selected)

        if selected:
            top = selected[0]
            print(f"  Episode {episode['episode_number']:>3}: "
                  f"{len(ep_candidates)} candidates → {len(selected)} non-overlapping | "
                  f"Best: {top['scores']['total']:.1f}")
        else:
            print(f"  Episode {episode['episode_number']:>3}: No strong candidates")

    candidates_path = os.path.join(output_dir, 'promo_candidates.json')
    with open(candidates_path, 'w', encoding='utf-8') as f:
        json.dump(all_candidates, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Found {len(all_candidates)} candidates. Saved: {candidates_path}")

    # ─── HYBRID MODE: Re-score top candidates with LLM ───────────
    if config.MODEL == 'hybrid':
        print(f"\n{'▶ ' * 3}STEP 2b: HYBRID LLM RE-SCORING{'◀ ' * 3}")
        print("-" * 50)

        # Pre-filter: take top 40 by heuristic score for LLM re-scoring
        pre_sorted = sorted(all_candidates,
                            key=lambda c: c['scores']['total'], reverse=True)
        top_for_llm = pre_sorted[:40]

        # Load the LLM model
        llm_model = get_model('gemini')  # or 'openai'
        print(f"   Re-scoring top {len(top_for_llm)} candidates with {llm_model.name}...")

        for i, cand in enumerate(top_for_llm):
            ep_num = cand['episode_number']
            episode = next(e for e in episodes if e['episode_number'] == ep_num)
            elements = episode['all_elements']
            episode_info = {
                'episode_number': ep_num,
                'logline': episode['logline'],
            }

            new_scores = llm_model.score_promo_candidate(
                elements, cand['start_time'], cand['end_time'], episode_info)

            # Blend: 40% heuristic + 60% LLM
            for key in ['hook', 'emotion', 'conflict', 'cliffhanger', 'standalone']:
                old = cand['scores'].get(key, 0)
                new = new_scores.get(key, 0)
                cand['scores'][key] = round(old * 0.4 + new * 0.6, 2)

            cand['scores']['total'] = round(sum(
                cand['scores'][k] for k in
                ['hook', 'emotion', 'conflict', 'cliffhanger', 'standalone']
            ), 2)
            cand['hook_text'] = new_scores.get('hook_text', cand['hook_text'])
            cand['cliffhanger_text'] = new_scores.get('cliffhanger_text',
                                                       cand['cliffhanger_text'])

            print(f"   [{i+1}/{len(top_for_llm)}] Ep {ep_num}: "
                  f"score {cand['scores']['total']:.1f}")
            time.sleep(0.5)  # Rate limit

        # Replace candidates with re-scored versions
        rescored_eps = {(c['episode_number'], c['start_time']): c for c in top_for_llm}
        for i, c in enumerate(all_candidates):
            key = (c['episode_number'], c['start_time'])
            if key in rescored_eps:
                all_candidates[i] = rescored_eps[key]

    # ─── STEP 3: RANK ─────────────────────────────────────────────
    print(f"\n{'▶ ' * 3}STEP 3: RANKING PROMOS{'◀ ' * 3}")
    print("-" * 50)

    ranked = model.rank_promos(all_candidates, config.TOP_N_PROMOS)

    print(f"\nTop {len(ranked)} Promos:")
    print(f"{'Rank':>4} | {'Ep':>3} | {'Time Range':<22} | {'Dur':>4} | "
          f"{'Score':>6} | Hook Preview")
    print("-" * 95)
    for p in ranked:
        hook_prev = (p.get('hook_text') or '')[:40]
        print(f"{p['rank']:>4} | {p['episode_number']:>3} | "
              f"{p['start_ts']} → {p['end_ts']} | "
              f"{p['duration']:>3}s | {p['rank_score']:>6.2f} | {hook_prev}")

    # Save JSON
    ranked_json = os.path.join(output_dir, 'ranked_promos.json')
    with open(ranked_json, 'w', encoding='utf-8') as f:
        json.dump(ranked, f, indent=2, ensure_ascii=False)

    # Save readable report
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append(f"PROMO RANKING REPORT")
    report_lines.append(f"Show: {show_name}")
    report_lines.append(f"Model: {config.MODEL}")
    report_lines.append("=" * 80)
    for p in ranked:
        report_lines.append(f"\n{'─' * 70}")
        report_lines.append(f"RANK #{p['rank']}")
        report_lines.append(f"{'─' * 70}")
        report_lines.append(f"Episode:     {p['episode_number']}")
        report_lines.append(f"Timestamps:  {p['start_ts']} → {p['end_ts']} ({p['duration']}s)")
        report_lines.append(f"Logline:     {p['logline'][:100]}...")
        report_lines.append(f"")
        report_lines.append(f"HOOK:        {(p.get('hook_text') or '')[:120]}")
        report_lines.append(f"CLIFFHANGER: {(p.get('cliffhanger_text') or '')[:120]}")
        report_lines.append(f"WHY IT WORKS: {p.get('why_it_works', 'N/A')}")
        report_lines.append(f"")
        s = p['scores']
        report_lines.append(f"SCORES: Hook={s['hook']}/15  Emotion={s['emotion']}/20  "
                            f"Conflict={s['conflict']}/15  Cliff={s['cliffhanger']}/10  "
                            f"Standalone={s['standalone']}/10  TOTAL={s['total']}/70  "
                            f"RANK={p['rank_score']:.3f}")
    report_lines.append(f"\n{'=' * 80}")
    report_lines.append("POSTING STRATEGY")
    report_lines.append("=" * 80)
    report_lines.append("POST FIRST (Ranks 1-5): Highest impact hooks and emotional peaks.")
    report_lines.append("POST NEXT (Ranks 6-10): Build the narrative curiosity.")
    report_lines.append("POST LATER (Ranks 11+): Sustain engagement.")

    ranked_txt = os.path.join(output_dir, 'ranked_promos_readable.txt')
    with open(ranked_txt, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    print(f"\n✅ Saved: {ranked_json}")
    print(f"✅ Saved: {ranked_txt}")

    # ─── STEP 4: QUALITY CHECK ────────────────────────────────────
    print(f"\n{'▶ ' * 3}STEP 4: QUALITY CHECK{'◀ ' * 3}")
    print("-" * 50)

    from quality_checker import (check_coverage, check_duration_distribution,
                                 check_hook_quality, check_cliffhanger_quality,
                                 identify_failure_modes, format_quality_report)

    coverage = check_coverage(ranked, total_episodes=len(episodes))
    duration_dist = check_duration_distribution(ranked)
    hooks = check_hook_quality(ranked)
    cliffs = check_cliffhanger_quality(ranked)
    failures = identify_failure_modes(ranked, all_candidates)

    quality_data = {
        'model_used': config.MODEL,
        'coverage': coverage,
        'duration_distribution': duration_dist,
        'hook_quality': hooks,
        'cliffhanger_quality': cliffs,
        'failure_modes': failures,
    }

    quality_json = os.path.join(output_dir, 'quality_report.json')
    with open(quality_json, 'w', encoding='utf-8') as f:
        json.dump(quality_data, f, indent=2, ensure_ascii=False)

    quality_txt = os.path.join(output_dir, 'quality_report.txt')
    report = format_quality_report(coverage, duration_dist, hooks, cliffs, failures)
    with open(quality_txt, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ Saved: {quality_json}")
    print(f"✅ Saved: {quality_txt}")

    # ─── DONE ─────────────────────────────────────────────────────
    elapsed = time.time() - start
    print(f"\n{'=' * 70}")
    print(f"  ✅ ALL STEPS COMPLETE in {elapsed:.1f} seconds")
    print(f"  📁 Results in: {output_dir}")
    print(f"  🎬 Model used: {config.MODEL}")
    print("=" * 70)

    return ranked


def main():
    args = parse_args()

    input_dir = resolve_input_dir(args.input)
    output_dir = args.output or os.path.join(SCRIPT_DIR, 'raw-outputs')

    run_pipeline(
        input_dir=input_dir,
        output_dir=output_dir,
        model_name=args.model,
        top_n=args.top,
        api_key=args.api_key
    )


if __name__ == '__main__':
    main()
