"""
STEP 4: QUALITY CHECKER
========================
This script evaluates how good our promo selections are by looking for
common failure modes, and produces an honest quality report.

WHAT IT CHECKS:
1. Coverage: Are we finding promos across many episodes or just a few?
2. Duration distribution: Are promos in the ideal 20-60s range?
3. Hook quality: Do top promos actually start with something dramatic?
4. Cliffhanger quality: Do they end on unresolved moments?
5. Failure analysis: Where does the tool pick badly?
6. Missed opportunities: Episodes with high drama but no promos selected

Output: ../raw-outputs/quality_report.txt
        ../raw-outputs/quality_report.json
"""

import os
import json
from collections import Counter


def check_coverage(ranked_promos, total_episodes=50):
    """Check how many episodes are covered by our promos."""
    covered = set(p['episode_number'] for p in ranked_promos)
    missing = set(range(1, total_episodes + 1)) - covered

    return {
        'episodes_covered': len(covered),
        'total_episodes': total_episodes,
        'coverage_pct': round(len(covered) / total_episodes * 100, 1),
        'covered_episodes': sorted(covered),
        'missing_episodes': sorted(missing),
        'assessment': (
            'GOOD' if len(covered) >= 10 else
            'FAIR' if len(covered) >= 5 else
            'POOR'
        )
    }


def check_duration_distribution(ranked_promos):
    """Check if promo durations are in the ideal range."""
    durations = [p['duration'] for p in ranked_promos]
    if not durations:
        return {'assessment': 'NO DATA'}

    avg = sum(durations) / len(durations)
    ideal = sum(1 for d in durations if 25 <= d <= 50)
    too_short = sum(1 for d in durations if d < 25)
    too_long = sum(1 for d in durations if d > 50)

    return {
        'average_duration': round(avg, 1),
        'min_duration': min(durations),
        'max_duration': max(durations),
        'ideal_range_count': ideal,
        'too_short_count': too_short,
        'too_long_count': too_long,
        'distribution': dict(Counter(durations)),
        'assessment': (
            'GOOD' if ideal >= len(durations) * 0.7 else
            'FAIR' if ideal >= len(durations) * 0.4 else
            'POOR'
        )
    }


def check_hook_quality(ranked_promos):
    """Check if hooks are actually strong."""
    hook_scores = [p['scores']['hook'] for p in ranked_promos]
    if not hook_scores:
        return {'assessment': 'NO DATA'}

    strong = sum(1 for s in hook_scores if s >= 6)
    weak = sum(1 for s in hook_scores if s < 3)

    weak_promos = []
    for p in ranked_promos:
        if p['scores']['hook'] < 3:
            weak_promos.append({
                'rank': p.get('rank', '?'),
                'episode': p['episode_number'],
                'hook_score': p['scores']['hook'],
                'hook_text': p['hook_text'][:80],
                'issue': 'Weak hook — may not stop a scrolling viewer'
            })

    return {
        'avg_hook_score': round(sum(hook_scores) / len(hook_scores), 2),
        'strong_hooks': strong,
        'weak_hooks': weak,
        'weak_promo_details': weak_promos,
        'assessment': (
            'GOOD' if strong >= len(ranked_promos) * 0.5 else
            'FAIR' if weak < len(ranked_promos) * 0.3 else
            'POOR'
        )
    }


def check_cliffhanger_quality(ranked_promos):
    """Check if cliffhangers are actually strong."""
    cliff_scores = [p['scores']['cliffhanger'] for p in ranked_promos]
    if not cliff_scores:
        return {'assessment': 'NO DATA'}

    strong = sum(1 for s in cliff_scores if s >= 5)
    weak = sum(1 for s in cliff_scores if s < 2)

    weak_promos = []
    for p in ranked_promos:
        if p['scores']['cliffhanger'] < 2:
            weak_promos.append({
                'rank': p.get('rank', '?'),
                'episode': p['episode_number'],
                'cliff_score': p['scores']['cliffhanger'],
                'cliff_text': p['cliffhanger_text'][:80],
                'issue': 'Weak cliffhanger — viewer may not feel compelled to watch more'
            })

    return {
        'avg_cliff_score': round(sum(cliff_scores) / len(cliff_scores), 2),
        'strong_cliffhangers': strong,
        'weak_cliffhangers': weak,
        'weak_promo_details': weak_promos,
        'assessment': (
            'GOOD' if strong >= len(ranked_promos) * 0.4 else
            'FAIR' if weak < len(ranked_promos) * 0.3 else
            'POOR'
        )
    }


def identify_failure_modes(ranked_promos, all_candidates):
    """Identify where the tool picks badly or misses opportunities."""
    failures = []

    # 1. Check for promos that might not make sense standalone
    for p in ranked_promos:
        if p['scores']['standalone'] < 4:
            failures.append({
                'type': 'LOW_STANDALONE',
                'rank': p.get('rank', '?'),
                'episode': p['episode_number'],
                'detail': 'This promo may not make sense to someone who hasn\'t seen the show. '
                          'It might rely on character knowledge or prior plot context.'
            })

    # 2. Check for promos where hook and cliffhanger are both weak
    for p in ranked_promos:
        if p['scores']['hook'] < 3 and p['scores']['cliffhanger'] < 3:
            failures.append({
                'type': 'WEAK_BOOKENDS',
                'rank': p.get('rank', '?'),
                'episode': p['episode_number'],
                'detail': 'Both the hook and cliffhanger are weak. The promo has middle drama '
                          'but doesn\'t grab attention at the start or leave the viewer hanging.'
            })

    # 3. Episodes with many candidates but none selected (potential misses)
    if all_candidates:
        ep_candidate_counts = Counter(c['episode_number'] for c in all_candidates)
        ep_selected = set(p['episode_number'] for p in ranked_promos)

        for ep, count in ep_candidate_counts.most_common(10):
            if ep not in ep_selected and count > 5:
                failures.append({
                    'type': 'MISSED_EPISODE',
                    'episode': ep,
                    'candidate_count': count,
                    'detail': f'Episode {ep} had {count} candidates but none were selected. '
                              f'The scoring may undervalue certain types of drama in this episode.'
                })

    # 4. Tool limitations (honest self-assessment)
    failures.append({
        'type': 'LIMITATION',
        'detail': 'The tool works on TEXT only — it cannot evaluate visual impact, '
                  'actor performance quality, or cinematographic appeal that a human editor sees.'
    })
    failures.append({
        'type': 'LIMITATION',
        'detail': 'Keyword-based scoring may miss subtle drama (quiet menace, loaded silences, '
                  'implied threats) that doesn\'t use explicitly dramatic vocabulary.'
    })
    failures.append({
        'type': 'LIMITATION',
        'detail': 'The tool cannot judge audio — music swells, sound effects, and voice tone '
                  'are major factors in promo effectiveness that text analysis misses.'
    })

    return failures


def format_quality_report(coverage, duration, hooks, cliffs, failures):
    """Format a human-readable quality report."""
    lines = []
    lines.append("=" * 80)
    lines.append("QUALITY CHECK REPORT")
    lines.append("Promo Finder Tool — Honest Self-Assessment")
    lines.append("=" * 80)
    lines.append("")

    # Overall grade
    grades = [coverage['assessment'], duration['assessment'],
              hooks['assessment'], cliffs['assessment']]
    good_count = grades.count('GOOD')
    overall = 'GOOD' if good_count >= 3 else 'FAIR' if good_count >= 1 else 'NEEDS WORK'

    lines.append(f"OVERALL ASSESSMENT: {overall}")
    lines.append("")

    # Coverage
    lines.append(f"{'─' * 60}")
    lines.append(f"1. EPISODE COVERAGE: {coverage['assessment']}")
    lines.append(f"{'─' * 60}")
    lines.append(f"   Episodes covered:  {coverage['episodes_covered']} / {coverage['total_episodes']} "
                 f"({coverage['coverage_pct']}%)")
    if coverage['missing_episodes']:
        missing = coverage['missing_episodes'][:10]
        lines.append(f"   Missing episodes:  {missing}" +
                     (" ..." if len(coverage['missing_episodes']) > 10 else ""))
    lines.append("")

    # Duration
    lines.append(f"{'─' * 60}")
    lines.append(f"2. DURATION DISTRIBUTION: {duration['assessment']}")
    lines.append(f"{'─' * 60}")
    if 'average_duration' in duration:
        lines.append(f"   Average duration:  {duration['average_duration']}s")
        lines.append(f"   Range:             {duration['min_duration']}s – {duration['max_duration']}s")
        lines.append(f"   In ideal range:    {duration['ideal_range_count']} promos")
        lines.append(f"   Too short (<25s):  {duration['too_short_count']} promos")
        lines.append(f"   Too long (>50s):   {duration['too_long_count']} promos")
    lines.append("")

    # Hooks
    lines.append(f"{'─' * 60}")
    lines.append(f"3. HOOK QUALITY: {hooks['assessment']}")
    lines.append(f"{'─' * 60}")
    if 'avg_hook_score' in hooks:
        lines.append(f"   Average hook score:  {hooks['avg_hook_score']} / 15")
        lines.append(f"   Strong hooks (≥6):   {hooks['strong_hooks']}")
        lines.append(f"   Weak hooks (<3):     {hooks['weak_hooks']}")
        if hooks['weak_promo_details']:
            lines.append(f"   Weak hook examples:")
            for wp in hooks['weak_promo_details'][:3]:
                lines.append(f"     - Rank #{wp['rank']}, Ep {wp['episode']}: {wp['issue']}")
    lines.append("")

    # Cliffhangers
    lines.append(f"{'─' * 60}")
    lines.append(f"4. CLIFFHANGER QUALITY: {cliffs['assessment']}")
    lines.append(f"{'─' * 60}")
    if 'avg_cliff_score' in cliffs:
        lines.append(f"   Average cliff score:   {cliffs['avg_cliff_score']} / 10")
        lines.append(f"   Strong cliffs (≥5):    {cliffs['strong_cliffhangers']}")
        lines.append(f"   Weak cliffs (<2):      {cliffs['weak_cliffhangers']}")
    lines.append("")

    # Failures
    lines.append(f"{'─' * 60}")
    lines.append(f"5. FAILURE MODES & LIMITATIONS")
    lines.append(f"{'─' * 60}")

    failure_types = {}
    for f in failures:
        ft = f['type']
        if ft not in failure_types:
            failure_types[ft] = []
        failure_types[ft].append(f)

    for ftype, items in failure_types.items():
        lines.append(f"\n   [{ftype}] ({len(items)} issues)")
        for item in items[:5]:
            lines.append(f"   • {item['detail']}")
    lines.append("")

    # Improvement suggestions
    lines.append(f"{'─' * 60}")
    lines.append(f"6. HOW TO IMPROVE")
    lines.append(f"{'─' * 60}")
    lines.append("   1. Add an LLM layer: Feed top candidates to GPT-4/Gemini for")
    lines.append("      semantic understanding of what makes a moment truly compelling.")
    lines.append("   2. Add visual analysis: Use video frames to score visual impact,")
    lines.append("      facial expressions, and cinematographic quality.")
    lines.append("   3. Cross-episode promos: Stitch dramatic moments from multiple")
    lines.append("      episodes into a single montage-style promo.")
    lines.append("   4. A/B test scoring weights: Run different weight configs and")
    lines.append("      compare with human editor picks to calibrate the model.")
    lines.append("   5. Viewer data feedback loop: Use engagement metrics from posted")
    lines.append("      promos to retrain the scoring weights.")
    lines.append("")

    return '\n'.join(lines)


def main():
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    ranked_path = os.path.join(project_dir, 'raw-outputs', 'ranked_promos.json')
    candidates_path = os.path.join(project_dir, 'raw-outputs', 'promo_candidates.json')
    report_txt = os.path.join(project_dir, 'raw-outputs', 'quality_report.txt')
    report_json = os.path.join(project_dir, 'raw-outputs', 'quality_report.json')

    # Load data
    print("Loading ranked promos...")
    with open(ranked_path, 'r', encoding='utf-8') as f:
        ranked_promos = json.load(f)

    all_candidates = []
    if os.path.exists(candidates_path):
        with open(candidates_path, 'r', encoding='utf-8') as f:
            all_candidates = json.load(f)
    print(f"Loaded {len(ranked_promos)} ranked promos, {len(all_candidates)} total candidates.\n")

    # Run checks
    print("Running quality checks...")
    coverage = check_coverage(ranked_promos)
    duration = check_duration_distribution(ranked_promos)
    hooks = check_hook_quality(ranked_promos)
    cliffs = check_cliffhanger_quality(ranked_promos)
    failures = identify_failure_modes(ranked_promos, all_candidates)

    # Build report
    quality_data = {
        'coverage': coverage,
        'duration_distribution': duration,
        'hook_quality': hooks,
        'cliffhanger_quality': cliffs,
        'failure_modes': failures,
    }

    # Save JSON report
    with open(report_json, 'w', encoding='utf-8') as f:
        json.dump(quality_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved quality report (JSON): {report_json}")

    # Save readable report
    report = format_quality_report(coverage, duration, hooks, cliffs, failures)
    with open(report_txt, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✅ Saved quality report (TXT):  {report_txt}")

    # Print summary
    print(f"\n{'=' * 50}")
    print(f"QUALITY SUMMARY")
    print(f"{'=' * 50}")
    print(f"  Coverage:     {coverage['assessment']} ({coverage['episodes_covered']}/{coverage['total_episodes']} episodes)")
    print(f"  Duration:     {duration['assessment']}")
    print(f"  Hooks:        {hooks['assessment']}")
    print(f"  Cliffhangers: {cliffs['assessment']}")
    print(f"  Failures:     {len(failures)} issues identified")

    return quality_data


if __name__ == '__main__':
    main()
