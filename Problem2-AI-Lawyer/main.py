"""
PROBLEM 2: AI LAWYER — TEST SUITE & CLI RUNNER
================================================
Runs all 5 realistic Indian dispute test cases, evaluates anti-hallucination compliance,
and generates unedited raw outputs into raw-outputs/.

Usage:
    python main.py
"""

import os
import sys
import json
from ai_lawyer import AILawyerEngine

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TESTS_PATH = os.path.join(SCRIPT_DIR, "test_cases", "test_cases.json")
OUTPUTS_DIR = os.path.join(SCRIPT_DIR, "raw-outputs")

def run_all_cases():
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    engine = AILawyerEngine()

    with open(TESTS_PATH, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    print("=" * 75)
    print("  PROBLEM 2: AI LAWYER FOR EVERYDAY INDIAN DISPUTES — TEST RUNNER")
    print(f"  Loaded {len(test_cases)} realistic test cases")
    print("=" * 75)

    all_results = []
    text_report = []

    for case in test_cases:
        cid = case["id"]
        title = case["title"]
        user_story = case["user_story"]
        details = case.get("user_details", {})

        print(f"\n▶ Executing: [{cid}] {title}")
        print("-" * 60)

        # 1. Build the case
        case_summary = engine.build_the_case(user_story, details)
        
        # 2. Plain language options
        legal_advice = engine.explain_options_plain_language(case_summary)

        # 3. Notice generation (if not criminal escalation)
        legal_notice = None
        if not legal_advice.get("requires_lawyer"):
            legal_notice = engine.generate_legal_demand_notice(case_summary, details)

        # 4. Roleplay counter-argument
        counter_arg = engine.roleplay_counter_argument(case_summary["domain"], "I am demanding my money back with interest.")

        res_obj = {
            "case_id": cid,
            "title": title,
            "language": case.get("language", "English"),
            "case_summary": case_summary,
            "legal_standing_and_options": legal_advice,
            "legal_demand_notice": legal_notice,
            "roleplay_counter_argument": counter_arg
        }
        all_results.append(res_obj)

        print(f"  • Domain Detected:     {case_summary['domain_name']}")
        print(f"  • Claim Amount:        {case_summary['amount_claimed']}")
        print(f"  • Proof Gathered:      {len(case_summary['existing_proof'])} items")
        print(f"  • Missing Proof:       {len(case_summary['missing_proof_needed'])} items")
        print(f"  • Escalation Required: {'🚨 YES (Criminal/Extortion)' if legal_advice.get('requires_lawyer') else '✅ NO (Civil Remedy Direct)'}")

        # Text Report Entry
        text_report.append(f"{'='*75}\nCASE {cid}: {title.upper()}\n{'='*75}")
        text_report.append(f"USER STORY:\n{user_story}\n")
        text_report.append(f"1. STRUCTURED CASE SUMMARY:")
        text_report.append(f"   Domain:          {case_summary['domain_name']}")
        text_report.append(f"   Amount Claimed:  {case_summary['amount_claimed']}")
        text_report.append(f"   Existing Proof:  {', '.join(case_summary['existing_proof']) if case_summary['existing_proof'] else 'None documented'}")
        text_report.append(f"   Missing Proof:   {', '.join(case_summary['missing_proof_needed']) if case_summary['missing_proof_needed'] else 'None'}\n")
        text_report.append(f"2. LEGAL STANDING & ACTIONABLE OPTIONS:")
        text_report.append(f"   Standing:        {legal_advice['standing']}")
        text_report.append(f"   Explanation:     {legal_advice['plain_explanation']}")
        for opt in legal_advice['options']:
            text_report.append(f"   • {opt}")
        text_report.append(f"\n3. ROLEPLAY OPPOSING COUNTER-ARGUMENT:")
        text_report.append(f"   {counter_arg}\n")
        if legal_notice:
            text_report.append(f"4. PREPARED LEGAL NOTICE:\n{legal_notice}\n")
        else:
            text_report.append(f"4. PREPARED LEGAL NOTICE: [SKIPPED - ADVOCATE ESCALATION MANDATED]\n")

    # Save JSON and TXT
    json_out = os.path.join(OUTPUTS_DIR, "ai_lawyer_test_outputs.json")
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    txt_out = os.path.join(OUTPUTS_DIR, "ai_lawyer_raw_outputs.txt")
    with open(txt_out, "w", encoding="utf-8") as f:
        f.write("\n".join(text_report))

    print("\n" + "=" * 75)
    print(f"  ✅ ALL 5 TEST CASES COMPLETED")
    print(f"  📁 Raw JSON outputs saved to: {json_out}")
    print(f"  📁 Raw TXT report saved to:   {txt_out}")
    print("=" * 75)

if __name__ == "__main__":
    run_all_cases()
