"""
STREAMLIT APP — AI LAWYER FOR EVERYDAY INDIAN DISPUTES
======================================================
Interactive conversational UI for ordinary citizens in India.
Supports English & Hinglish, builds structured cases, explains legal options,
generates downloadable Legal Demand Notices, and practices opposing negotiations.

Run with:
    streamlit run app.py
"""

import os
import sys
import json
import streamlit as st

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from ai_lawyer import AILawyerEngine

st.set_page_config(
    page_title="NyayaAI — Everyday Legal Assistant for India",
    page_icon="⚖️",
    layout="wide"
)

# Load test cases for quick demo
TEST_CASES_PATH = os.path.join(SCRIPT_DIR, "test_cases", "test_cases.json")
test_cases = []
if os.path.exists(TEST_CASES_PATH):
    with open(TEST_CASES_PATH, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

engine = AILawyerEngine()

# Custom Header
st.title("⚖️ NyayaAI — Everyday Legal Helper for India")
st.caption("Grounded, honest legal support for rent deposits, e-commerce refunds, unpaid salaries, and consumer grievances.")

with st.sidebar:
    st.header("⚡ Load Sample Dispute")
    sample_titles = ["-- Type My Own Story --"] + [c["title"] for c in test_cases]
    chosen_sample = st.selectbox("Select a realistic scenario:", sample_titles)
    
    st.markdown("---")
    st.markdown("### 🛡️ Ground Rules & Ethics")
    st.markdown("""
    - **Zero Hallucinated Laws:** Only cites verified statutory acts (Transfer of Property Act, Consumer Protection Act, Payment of Wages Act).
    - **No Fake Court Precedents:** Never invents fictitious case citations.
    - **Advocate Escalation:** Immediately warns and redirects when criminal threats or court litigation is required.
    """)

# Pre-populate if sample selected
initial_text = ""
initial_details = {}
if chosen_sample != "-- Type My Own Story --":
    for c in test_cases:
        if c["title"] == chosen_sample:
            initial_text = c["user_story"]
            initial_details = c.get("user_details", {})
            break

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Tell Your Story (English / Hinglish / Hindi)")
    user_story = st.text_area(
        "Describe what happened in your own words:",
        value=initial_text,
        height=220,
        placeholder="e.g. Maine flat khali kiya 1 month pehle par landlord deposit return nahi kar raha..."
    )
    
    analyze_btn = st.button("🚀 Analyze My Case & Generate Action Plan", type="primary")

if analyze_btn and user_story.strip():
    with col2:
        st.subheader("2. Legal Standing & Case Analysis")
        
        # 1. Build the case
        case_summary = engine.build_the_case(user_story, initial_details)
        legal_advice = engine.explain_options_plain_language(case_summary)
        
        # Check escalation
        if legal_advice.get("requires_lawyer"):
            st.error("🚨 CRITICAL ALERT: ADVOCATE / POLICE ESCALATION MANDATED")
            st.warning(legal_advice["plain_explanation"])
            st.markdown("**Urgent Steps You Must Take:**")
            for opt in legal_advice["options"]:
                st.markdown(f"• **{opt}**")
        else:
            st.success(f"✅ Domain Identified: {case_summary['domain_name']}")
            
            m1, m2 = st.columns(2)
            m1.metric("Financial Stake", case_summary["amount_claimed"])
            m2.metric("Evidence Status", f"{len(case_summary['existing_proof'])} Proof Gathered")
            
            with st.expander("📋 Structured Case Breakdown", expanded=True):
                st.markdown(f"**Legal Grounding:** *{legal_advice['standing']}*")
                st.markdown(f"**Plain Language Assessment:** {legal_advice['plain_explanation']}")
                
                st.markdown("**Evidence in your possession:**")
                if case_summary["existing_proof"]:
                    for p in case_summary["existing_proof"]:
                        st.markdown(f"✅ {p}")
                else:
                    st.caption("No explicit proof mentioned in your story.")
                    
                st.markdown("**Missing proof you should organize:**")
                for p in case_summary["missing_proof_needed"]:
                    st.markdown(f"⚠️ {p}")

            st.markdown("### 🛠️ What You Can Do Right Now:")
            for opt in legal_advice["options"]:
                st.markdown(f"👉 **{opt}**")
                
            # Notice tab
            legal_notice = engine.generate_legal_demand_notice(case_summary, initial_details)
            st.markdown("### 📄 Draft Legal Demand Notice (15-Day Cure Period)")
            st.code(legal_notice, language="text")
            st.download_button(
                "📥 Download Legal Notice (.txt)",
                data=legal_notice,
                file_name=f"Legal_Demand_Notice_{case_summary['domain']}.txt",
                mime="text/plain"
            )

    # Opposing argument practice
    st.markdown("---")
    st.subheader("3. Practice Arguing (Negotiation Simulator)")
    st.caption("The AI plays the difficult landlord, merchant, or employer so you can practice your points before sending notice.")
    
    sim_col1, sim_col2 = st.columns([1, 1])
    with sim_col1:
        user_pitch = st.text_input("Say something to the other party:", value="I am giving you 15 days to refund my full deposit before I approach the Rent Authority.")
        sim_btn = st.button("Simulate Opposing Response")
    
    with sim_col2:
        if sim_btn and user_pitch:
            counter = engine.roleplay_counter_argument(case_summary["domain"], user_pitch)
            st.warning(counter)
            st.info("💡 **Coach Tip:** Stay calm and stick to documentary facts (inspection report, payment receipt) rather than emotional arguments.")
