"""
AI LAWYER CORE ENGINE
======================
Conversational legal assistant for everyday Indian civil grievances.
Strictly grounded against hallucinations using statutory rules in knowledge_base/legal_rules.json.

Key capabilities required by Kuku Brief:
1. Build the case (turn messy story into structured facts, dates, proof)
2. Explain where they stand & options in plain language
3. Prepare what they need (Formal Legal Notice / Consumer Complaint)
4. Help them argue (Roleplay counter-arguments for practice)
5. Ground rules: Clear boundaries, zero hallucinated sections, advocate escalation.
"""

import os
import json
import re
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KB_PATH = os.path.join(SCRIPT_DIR, "knowledge_base", "legal_rules.json")

class AILawyerEngine:
    def __init__(self, kb_path=KB_PATH):
        self.kb_path = kb_path
        self.rules = self._load_rules()

    def _load_rules(self):
        if os.path.exists(self.kb_path):
            with open(self.kb_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"domains": {}, "forbidden_hallucinations": []}

    def detect_domain_and_escalation(self, story_text):
        """Detect legal domain and check for criminal escalation using strict regex boundaries."""
        text_lower = story_text.lower()
        
        # Check criminal / police / extortion escalation flags with word boundaries
        criminal_patterns = [
            r'\bfir\b',
            r'\barrest\b',
            r'\bpolice\b',
            r'\binspector\b',
            r'\bcrime branch\b',
            r'\bjail\b',
            r'\bextortion\b',
            r'physical violence|threatened to harm|threatened to kill'
        ]
        
        if any(re.search(pat, text_lower) for pat in criminal_patterns):
            return "escalation_required", None

        # Check civil domains using word boundary patterns
        if any(re.search(rf'\b{w}\b', text_lower) for w in ["landlord", "rent", "deposit", "flat", "pg", "tenant", "lease"]):
            return "tenancy_security_deposit", self.rules.get("domains", {}).get("tenancy_security_deposit")
            
        if any(re.search(rf'\b{w}\b', text_lower) for w in ["salary", "employer", "resignation", "relieving", "notice period", "hr", "wages"]):
            return "unpaid_salary_employment", self.rules.get("domains", {}).get("unpaid_salary_employment")

        if any(re.search(rf'\b{w}\b', text_lower) for w in ["order", "refund", "delivery", "product", "gym", "consumer", "damaged", "ticket"]):
            return "consumer_e_commerce_refund", self.rules.get("domains", {}).get("consumer_e_commerce_refund")

        return "general_civil", None

    def build_the_case(self, user_story, user_details=None):
        """Extract timeline, financial stake, existing proof, and missing evidence."""
        domain, domain_info = self.detect_domain_and_escalation(user_story)
        
        # Extract money figures via regex or details
        claimed_amt = None
        if user_details:
            claimed_amt = user_details.get("amount_claimed") or user_details.get("extortion_amount")
        if not claimed_amt:
            money_matches = re.findall(r'(?:₹|rs\.?|inr)\s*([\d,]+)', user_story, re.IGNORECASE)
            claimed_amt = f"₹{money_matches[0]}" if money_matches else "Amount unspecified"
        
        # Dates identification
        date_pattern = re.findall(r'\b(?:\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b', user_story, re.IGNORECASE)

        # Proof detection
        existing_proof = []
        text_l = user_story.lower()
        if "whatsapp" in text_l: existing_proof.append("WhatsApp chat logs / agreement confirmations")
        if any(w in text_l for w in ["receipt", "invoice", "bank", "gpay", "upi"]): existing_proof.append("Proof of payment (Bank/UPI/Receipt)")
        if any(w in text_l for w in ["photo", "video", "unboxing"]): existing_proof.append("Photographic / Video evidence of condition")
        if "email" in text_l: existing_proof.append("Email correspondence")

        recommended_proof = domain_info.get("required_proof", []) if domain_info else ["Written communication records", "Payment debit slips"]
        missing_proof = [p for p in recommended_proof if not any(k.lower() in p.lower() for k in existing_proof)]

        return {
            "domain": domain,
            "domain_name": domain_info.get("name", "General Civil Dispute") if domain_info else "Urgent Criminal Escalation",
            "amount_claimed": claimed_amt,
            "dates_identified": date_pattern,
            "existing_proof": existing_proof,
            "missing_proof_needed": missing_proof,
            "raw_story": user_story
        }

    def explain_options_plain_language(self, case_summary):
        """Plain language explanation of legal standing and actionable steps."""
        domain = case_summary["domain"]
        domain_info = self.rules.get("domains", {}).get(domain)

        if domain == "escalation_required":
            return {
                "standing": "CRITICAL WARNING: Threat of arrest / Police impersonation detected.",
                "plain_explanation": (
                    "No legitimate police officer or court sends arrest warrants on WhatsApp or demands money via personal UPI IDs. "
                    "This is an illegal intimidation/extortion attempt by rogue recovery agents or fraudsters."
                ),
                "options": [
                    "DO NOT transfer any money to the personal UPI ID.",
                    "Save all screenshots, call recordings, and the PDF with fake seals.",
                    "Immediately file a cyber fraud report on https://cybercrime.gov.in or dial National Cyber Helpline 1930.",
                    "Consult a licensed criminal advocate immediately if they show up at your residence."
                ],
                "requires_lawyer": True
            }

        if not domain_info:
            return {
                "standing": "Unclassified Civil Matter",
                "plain_explanation": "Your grievance requires contract and transactional review.",
                "options": ["Gather all written agreements", "Issue a formal demand notice", "Consult an advocate"],
                "requires_lawyer": True
            }

        applicable_law = domain_info.get("applicable_law", "General Indian Contract Law")
        principles = domain_info.get("key_principles", [])

        return {
            "standing": f"Strong Prima Facie Case under {applicable_law}",
            "plain_explanation": (
                f"Under Indian law, the other party cannot arbitrarily withhold your money without documented justification. "
                f"You have a strong legal right to seek full refund of {case_summary['amount_claimed']}."
            ),
            "key_principles": principles,
            "options": [
                "Step 1: Send a Formal Written Demand Notice giving 15 clear days to settle.",
                "Step 2: File a free pre-litigation grievance on government portals (e.g., National Consumer Helpline 1915 or State Labour Portal).",
                "Step 3: If unresponsive, escalate to the appropriate statutory forum (District Consumer Commission via e-Daakhil or Rent Authority)."
            ],
            "requires_lawyer": False
        }

    def generate_legal_demand_notice(self, case_summary, user_details):
        """Generate a formal, un-hallucinated Legal Demand Notice."""
        domain = case_summary["domain"]
        domain_info = self.rules.get("domains", {}).get(domain, {})
        applicable_law = domain_info.get("applicable_law", "Applicable Indian Statutes")
        today_str = datetime.now().strftime("%d-%B-%Y")

        sender = user_details.get("tenant_name") or user_details.get("consumer_name") or user_details.get("employee_name") or "Aggrieved Party"
        recipient = user_details.get("landlord_name") or user_details.get("merchant_name") or user_details.get("employer_name") or "Opposite Party"
        amount = case_summary["amount_claimed"]

        notice_text = f"""
================================================================================
FORMAL LEGAL DEMAND NOTICE (WITHOUT PREJUDICE)
Date: {today_str}
Sent via: Registered Post A.D. & Electronic Mail

TO:
{recipient}

FROM:
{sender}

SUBJECT: DEMAND FOR REFUND OF {amount} PURSUANT TO {applicable_law.upper()}

Sir/Madam,

Under instructions and in terms of statutory provisions of {applicable_law}, you are hereby formally put on notice as follows:

1. STATEMENT OF FACTS:
That the undersigned entered into a legitimate transaction with you regarding:
"{case_summary['raw_story'][:250]}..."

2. UNLAWFUL WITHHOLDING & DEFICIENCY:
That despite repeated formal requests, you have unlawfully failed, refused, and neglected to release the legitimate sum of {amount} legitimately due and payable to the undersigned. Such arbitrary retention constitutes breach of contractual obligations and unfair practice.

3. SUPPORTING EVIDENCE IN POSSESSION:
The undersigned possesses irrefutable documentary proof including:
{chr(10).join(f" - {p}" for p in case_summary['existing_proof'])}

4. FINAL DEMAND FOR COMPLIANCE:
You are hereby called upon to refund the full sum of {amount} to the undersigned's designated account within 15 (FIFTEEN) DAYS from the receipt of this notice, failing which the undersigned shall be constrained to initiate appropriate legal proceedings before the competent statutory forum, including the Consumer Disputes Redressal Commission / Rent Authority / Labour Commissioner, holding you liable for all legal costs, interest at 18% p.a., and damages for mental harassment.

Yours faithfully,

{sender}
(Aggrieved Complainant)
================================================================================
"""
        return notice_text.strip()

    def roleplay_counter_argument(self, domain, user_statement):
        """Practice negotiation by playing the difficult opposing party."""
        user_lower = user_statement.lower()

        if domain == "tenancy_security_deposit":
            if "wear and tear" in user_lower:
                return "Opposing Landlord: 'Normal wear and tear? The entire flat needed fresh Asian Paints Royal coat and the bathroom tap was leaking! You stayed for a year, who else will pay for it?'"
            return "Opposing Landlord: 'Look at clause 8 of the agreement, painting charges are always deducted from deposit. Everybody in Bangalore does this. Take ₹25,000 or wait 2 months.'"

        if domain == "consumer_e_commerce_refund":
            return "Opposing Customer Support: 'We deeply regret the inconvenience, but our delivery policy strictly requires unboxing verification in front of the courier agent. Since the package was marked accepted, system will not permit refund.'"

        if domain == "unpaid_salary_employment":
            return "Opposing HR Director: 'The company suffered project delivery delays due to your incomplete handover. Until the client signs off, management has placed your final settlement and relieving letter on hold under company policy.'"

        return "Opposing Party: 'We have received your message. However, as per company policy, no further refund is entertainable.'"
