"""
STEP 3: PROMO RANKER
====================
This script takes all promo candidates from Step 2 and produces a final
ranked list of the TOP promos you would actually post on social media.

HOW IT WORKS:
1. Loads all promo candidates
2. Applies a composite ranking formula:
   - 30% Hook score (first impressions matter most on social)
   - 25% Emotion score (emotional content gets shared)
   - 20% Conflict score (drama drives engagement)
   - 15% Cliffhanger score (makes viewers want to watch the show)
   - 10% Standalone score (must make sense without context)
3. Applies bonus/penalty adjustments:
   - Bonus for variety (different episodes over repeating same one)
   - Bonus for optimal duration (30-45s is the sweet spot)
   - Penalty for being too short or too long
4. Outputs the final ranked list with posting order

Output: ../raw-outputs/ranked_promos.json
        ../raw-outputs/ranked_promos_readable.txt
"""

import os
import json


def compute_final_rank_score(candidate):
    """Compute weighted final ranking score."""
    scores = candidate['scores']

    # Weighted composite
    weighted = (
        scores['hook'] * 0.30 +
        scores['emotion'] * 0.25 +
        scores['conflict'] * 0.20 +
        scores['cliffhanger'] * 0.15 +
        scores['standalone'] * 0.10
    )

    # Duration bonus: 30-45 seconds is the sweet spot for social media
    duration = candidate['duration']
    if 30 <= duration <= 45:
        weighted *= 1.10  # 10% bonus
    elif duration < 20 or duration > 55:
        weighted *= 0.90  # 10% penalty

    # Dialogue density bonus: promos with good dialogue are more engaging
    if candidate['dialogue_count'] >= 4:
        weighted *= 1.05

    return round(weighted, 3)


def diversify_selection(ranked_candidates, max_per_episode=3, top_n=20):
    """
    Select top promos while ensuring episode diversity.
    We don't want 10 promos from the same episode.
    """
    episode_counts = {}
    diversified = []

    for candidate in ranked_candidates:
        ep = candidate['episode_number']
        count = episode_counts.get(ep, 0)

        if count < max_per_episode:
            diversified.append(candidate)
            episode_counts[ep] = count + 1

        if len(diversified) >= top_n:
            break

    return diversified


def generate_why_it_works(candidate):
    """Generate a human-readable explanation of why this promo works."""
    scores = candidate['scores']
    reasons = []

    if scores['hook'] >= 6:
        reasons.append("Strong opening hook that stops scrollers")
    elif scores['hook'] >= 3:
        reasons.append("Decent attention-grabbing opening")

    if scores['emotion'] >= 10:
        reasons.append("Extremely high emotional intensity")
    elif scores['emotion'] >= 6:
        reasons.append("Strong emotional dialogue")

    if scores['conflict'] >= 8:
        reasons.append("Intense conflict/confrontation")
    elif scores['conflict'] >= 4:
        reasons.append("Clear dramatic tension")

    if scores['cliffhanger'] >= 6:
        reasons.append("Powerful cliffhanger ending")
    elif scores['cliffhanger'] >= 3:
        reasons.append("Leaves viewer wanting more")

    if scores['standalone'] >= 7:
        reasons.append("Self-explanatory to new viewers")

    if not reasons:
        reasons.append("Moderate dramatic content suitable for promo")

    return "; ".join(reasons)


def format_readable_output(ranked_promos):
    """Create a human-readable text report of the ranked promos."""
    lines = []
    lines.append("=" * 80)
    lines.append("PROMO RANKING REPORT")
    lines.append("Show: I Married a Broken Soldier. He was a Duke")
    lines.append("=" * 80)
    lines.append("")

    for i, promo in enumerate(ranked_promos, 1):
        lines.append(f"{'─' * 70}")
        lines.append(f"RANK #{i}")
        lines.append(f"{'─' * 70}")
        lines.append(f"Episode:     {promo['episode_number']}")
        lines.append(f"Timestamps:  {promo['start_ts']} → {promo['end_ts']} "
                      f"({promo['duration']}s)")
        lines.append(f"Logline:     {promo['logline'][:100]}...")
        lines.append(f"")
        lines.append(f"HOOK:        {promo['hook_text'][:120]}")
        lines.append(f"CLIFFHANGER: {promo['cliffhanger_text'][:120]}")
        lines.append(f"")
        lines.append(f"WHY IT WORKS: {promo['why_it_works']}")
        lines.append(f"")
        lines.append(f"SCORES:")
        lines.append(f"  Hook:         {promo['scores']['hook']:>5.1f} / 15")
        lines.append(f"  Emotion:      {promo['scores']['emotion']:>5.1f} / 20")
        lines.append(f"  Conflict:     {promo['scores']['conflict']:>5.1f} / 15")
        lines.append(f"  Cliffhanger:  {promo['scores']['cliffhanger']:>5.1f} / 10")
        lines.append(f"  Standalone:   {promo['scores']['standalone']:>5.1f} / 10")
        lines.append(f"  TOTAL:        {promo['scores']['total']:>5.1f} / 70")
        lines.append(f"  RANK SCORE:   {promo['rank_score']:>5.3f}")
        lines.append(f"")

    lines.append("=" * 80)
    lines.append(f"POSTING STRATEGY")
    lines.append("=" * 80)
    lines.append("")
    lines.append("POST FIRST (Ranks 1-5): Highest impact hooks and emotional peaks.")
    lines.append("  These promos have the strongest opening hooks and most intense")
    lines.append("  confrontations — perfect for the initial promotional push.")
    lines.append("")
    lines.append("POST NEXT (Ranks 6-10): Build the narrative curiosity.")
    lines.append("  These promos reveal different character dynamics and subplots,")
    lines.append("  giving viewers a broader taste of the show's world.")
    lines.append("")
    lines.append("POST LATER (Ranks 11+): Sustain engagement.")
    lines.append("  Use these for ongoing promotion, targeting audiences who've")
    lines.append("  already seen earlier promos and want more.")
    lines.append("")

    return '\n'.join(lines)


def main():
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    input_path = os.path.join(project_dir, 'raw-outputs', 'promo_candidates.json')
    output_json = os.path.join(project_dir, 'raw-outputs', 'ranked_promos.json')
    output_txt = os.path.join(project_dir, 'raw-outputs', 'ranked_promos_readable.txt')

    # Load candidates
    print("Loading promo candidates...")
    with open(input_path, 'r', encoding='utf-8') as f:
        candidates = json.load(f)
    print(f"Loaded {len(candidates)} candidates.\n")

    # Compute final ranking score for each
    print("Computing ranking scores...")
    for c in candidates:
        c['rank_score'] = compute_final_rank_score(c)
        c['why_it_works'] = generate_why_it_works(c)

    # Sort by rank score
    candidates.sort(key=lambda c: c['rank_score'], reverse=True)

    # Diversify — get top 20 with max 3 per episode
    top_promos = diversify_selection(candidates, max_per_episode=3, top_n=20)

    # Re-rank after diversification
    for i, promo in enumerate(top_promos, 1):
        promo['rank'] = i

    print(f"\nTop {len(top_promos)} Promos (diversified across episodes):")
    print(f"{'Rank':>4} | {'Ep':>3} | {'Time Range':<20} | {'Duration':>4} | {'Score':>6} | Hook Preview")
    print("-" * 90)
    for p in top_promos:
        hook_preview = p['hook_text'][:40]
        print(f"{p['rank']:>4} | {p['episode_number']:>3} | "
              f"{p['start_ts']} → {p['end_ts']} | "
              f"{p['duration']:>3}s | {p['rank_score']:>6.2f} | {hook_preview}")

    # Save JSON
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(top_promos, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Saved ranked promos (JSON): {output_json}")

    # Save readable report
    report = format_readable_output(top_promos)
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✅ Saved readable report:      {output_txt}")

    return top_promos


if __name__ == '__main__':
    main()
