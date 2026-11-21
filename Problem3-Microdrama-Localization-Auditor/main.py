"""
PROBLEM 3: MICRODRAMA PACING & LOCALIZATION AUDITOR — BATCH RUNNER
==================================================================
Audits all 50 episodes from the input pack to detect dialogue velocity violations
(rushed/dragged speech) and dead air retention drop-offs (>3s gaps).

Outputs saved to raw-outputs/
Usage:
    python main.py
"""

import os
import sys
import json
import glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'auditor'))

from pacing_auditor import audit_episode_screenplay

def run_full_audit():
    parent_dir = os.path.dirname(SCRIPT_DIR)
    input_dir = os.path.join(parent_dir, "I Married a Broken Soldier. He was a Duke")
    output_dir = os.path.join(SCRIPT_DIR, "raw-outputs")
    os.makedirs(output_dir, exist_ok=True)

    files = sorted(glob.glob(os.path.join(input_dir, "episode-*.txt")))
    print("=" * 80)
    print("  PROBLEM 3: MICRODRAMA PACING & LOCALIZATION AUDITOR")
    print(f"  Target: {len(files)} Screenplays from 'I Married a Broken Soldier. He was a Duke'")
    print("=" * 80)

    all_audits = []
    total_rushed = 0
    total_dragged = 0
    total_dead_air = 0

    print(f"{'Ep':>3} | {'Health':>6} | {'Lines':>5} | {'Rushed':>6} | {'Dragged':>7} | {'Dead Air':>8} | Status")
    print("-" * 80)

    for fp in files:
        audit = audit_episode_screenplay(fp)
        all_audits.append(audit)

        rushed_count = sum(1 for i in audit['dialogue_issues'] if i['type'] == 'UNNATURALLY_RUSHED')
        dragged_count = sum(1 for i in audit['dialogue_issues'] if i['type'] == 'UNNATURALLY_DRAGGED')
        dead_air_count = len(audit['dead_air_gaps'])

        total_rushed += rushed_count
        total_dragged += dragged_count
        total_dead_air += dead_air_count

        status = "✅ CLEAN" if audit['health_score'] >= 80 else ("⚠️ RE-TIME" if audit['health_score'] >= 60 else "🚨 CRITICAL")

        print(f"{audit['episode_number']:>3} | {audit['health_score']:>5}% | {audit['total_dialogues']:>5} | {rushed_count:>6} | {dragged_count:>7} | {dead_air_count:>8} | {status}")

    # Save JSON and TXT
    json_path = os.path.join(output_dir, "localization_pacing_audit.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_audits, f, indent=2, ensure_ascii=False)

    # Readable QA report
    txt_path = os.path.join(output_dir, "localization_pacing_report.txt")
    lines = [
        "=" * 80,
        "MICRODRAMA LOCALIZATION & PACING AUDIT REPORT",
        "Show: I Married a Broken Soldier. He was a Duke (50 Episodes)",
        "=" * 80,
        f"Total Episodes Audited:          50",
        f"Total Speech Velocity Anomalies: {total_rushed + total_dragged} ({total_rushed} rushed, {total_dragged} dragged)",
        f"Total Dead Air Retention Gaps:   {total_dead_air} (>3.2s silence)",
        "=" * 80,
        ""
    ]

    for a in all_audits:
        if a['dialogue_issues'] or a['dead_air_gaps']:
            lines.append(f"\n{'─'*70}")
            lines.append(f"EPISODE {a['episode_number']} (Health Score: {a['health_score']}%)")
            lines.append(f"Logline: {a['logline'][:90]}...")
            lines.append(f"{'─'*70}")

            if a['dialogue_issues']:
                lines.append("  [SPEECH VELOCITY DEFECTS]:")
                for iss in a['dialogue_issues'][:4]:
                    lines.append(f"   • [{iss['start_ts']} - {iss['end_ts']}] ({iss['wpm']} WPM) {iss['speaker']}: \"{iss['text'][:60]}...\"")
                    lines.append(f"     ➔ Action Required: {iss['recommendation']}")

            if a['dead_air_gaps']:
                lines.append("  [DEAD AIR RETENTION HAZARDS]:")
                for gap in a['dead_air_gaps'][:3]:
                    lines.append(f"   • {gap['gap_duration']}s gap between {gap['from_ts']} and {gap['to_ts']} ({gap['between_speakers']})")
                    lines.append(f"     Intermediate: {gap['intermediate_action']}")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("\n" + "=" * 80)
    print(f"  ✅ AUDIT COMPLETE ACROSS ALL 50 EPISODES")
    print(f"  • Total Rushed Lines (&gt;185 WPM): {total_rushed}")
    print(f"  • Total Dragged Lines (&lt;65 WPM): {total_dragged}")
    print(f"  • Dead Air Gaps (&gt;3.2s):         {total_dead_air}")
    print(f"  📁 Raw JSON: {json_path}")
    print(f"  📁 Raw Report: {txt_path}")
    print("=" * 80)

if __name__ == "__main__":
    run_full_audit()
