"""
STREAMLIT APP — MICRODRAMA PACING & LOCALIZATION AUDITOR
========================================================
Interactive QA dashboard for Localization Directors, Dubbing Leads, and Audio Editors.
Visualizes speech velocity anomalies (WPM) and dead air retention hazards (>3s)
across all 50 episodes.

Run with:
    streamlit run app.py
"""

import os
import sys
import json
import streamlit as st

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'auditor'))

st.set_page_config(
    page_title="Kuku Microdrama Pacing & Localization Auditor",
    page_icon="⏱️",
    layout="wide"
)

# Load audit data
AUDIT_JSON = os.path.join(SCRIPT_DIR, "raw-outputs", "localization_pacing_audit.json")

@st.cache_data
def load_audit():
    if os.path.exists(AUDIT_JSON):
        with open(AUDIT_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

audits = load_audit()

st.title("⏱️ Kuku Microdrama Pacing & Localization Auditor")
st.caption("Automated QA to eliminate rushed dubbing (>185 WPM) and algorithmic dead air (>3.2s) in vertical microdramas.")

if not audits:
    st.warning("Audit data not found. Please run `python main.py` first.")
else:
    # Top KPI Metrics
    total_eps = len(audits)
    avg_health = sum(a['health_score'] for a in audits) / total_eps
    total_rushed = sum(sum(1 for i in a['dialogue_issues'] if i['type'] == 'UNNATURALLY_RUSHED') for a in audits)
    total_gaps = sum(len(a['dead_air_gaps']) for a in audits)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Catalog Health", f"{avg_health:.1f}%", "Target > 80%")
    c2.metric("Rushed Lines (>185 WPM)", total_rushed, "Causes AI Dub Clipping")
    c3.metric("Dead Air Retention Gaps", total_gaps, ">3.2s Silent Drops")
    c4.metric("Episodes Audited", total_eps, "50 / 50 Screenplays")

    st.markdown("---")

    # Episode selector
    ep_options = [f"Episode {a['episode_number']} (Health: {a['health_score']}%)" for a in audits]
    chosen_ep_label = st.selectbox("Select Episode to inspect:", ep_options)
    ep_num = int(chosen_ep_label.split(" ")[1])
    selected_audit = next(a for a in audits if a['episode_number'] == ep_num)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader(f"🎬 Episode {selected_audit['episode_number']} Overview")
        st.info(f"**Logline:** {selected_audit['logline']}")
        st.progress(selected_audit['health_score'] / 100.0, text=f"Episode Pacing Health Score: {selected_audit['health_score']}%")

        st.markdown("### 🗣️ Dialogue Velocity Defects (WPM Anomalies)")
        if not selected_audit['dialogue_issues']:
            st.success("✅ No speech velocity anomalies detected in this episode.")
        else:
            for issue in selected_audit['dialogue_issues']:
                with st.expander(f"⚠️ [{issue['start_ts']} - {issue['end_ts']}] {issue['speaker']} ({issue['wpm']} WPM | {issue['duration']}s)", expanded=True):
                    st.markdown(f"**Line:** *\"{issue['text']}\"*")
                    st.markdown(f"**Emotion Tag:** `{issue['emotion']}`")
                    st.markdown(f"**Word Count:** {issue['word_count']} words in {issue['duration']} seconds")
                    st.error(f"👉 **Fix:** {issue['recommendation']}")

    with col_right:
        st.subheader("⏸️ Dead Air Retention Hazards (>3.2s)")
        if not selected_audit['dead_air_gaps']:
            st.success("✅ Clean pacing! No dead air gaps over 3.2 seconds.")
        else:
            for gap in selected_audit['dead_air_gaps']:
                with st.expander(f"🚨 {gap['gap_duration']}s Silence: {gap['between_speakers']} ({gap['from_ts']} ➔ {gap['to_ts']})", expanded=True):
                    st.markdown(f"**Risk Level:** `{gap['risk']}`")
                    st.markdown(f"**Script Activity:** *{gap['intermediate_action']}*")
                    st.warning("👉 **Editor Action:** Insert sound FX drone or tighten scene cut to maintain algorithmic TikTok watch-time.")

    st.markdown("---")
    st.subheader("💡 Why This Problem Matters More Than 1 & 2")
    st.markdown("""
    - **Algorithmic Watch Time:** In vertical short-form video (TikTok, YouTube Shorts, Kuku TV), algorithmic distribution is 90% driven by **completion rate**.
    - If a voiceover rushes at 210 WPM, user comprehension drops and they exit.
    - If a 4-second silence occurs on screen without audio punch, mobile users swipe to the next video.
    - **Production Impact:** Running this 1-second automated audit *before* voice actors record or AI text-to-speech models render saves hundreds of audio re-take hours.
    """)
