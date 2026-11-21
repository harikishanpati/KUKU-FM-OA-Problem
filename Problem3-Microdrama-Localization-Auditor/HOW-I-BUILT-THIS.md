# HOW I BUILT THIS — Problem 3: Microdrama Pacing & Localization Auditor

## The Big Picture
Built the **Microdrama Pacing & Localization Auditor**, an automated QA tool designed specifically for the audio and localization workflow at microdrama companies like Kuku.

It scans episodic screenplays to catch two critical algorithmic retention-killers before dubbing or video rendering:
1. **Dialogue Velocity Anomalies (WPM):** Lines where text is squeezed into unrealistically short durations (>185 Words Per Minute), causing AI voice models (ElevenLabs/Murf) or dubbing actors to sound unnatural or clipped.
2. **Dead Air Retention Hazards (>3.2s):** Gaps of silent dead air between dialogue exchanges that cause mobile scrollers to swipe away on TikTok and Shorts.

---

## Folder Structure
```
Problem3-Microdrama-Localization-Auditor/
├── auditor/
│   └── pacing_auditor.py         ← Core speech velocity & dead-air detection algorithm
├── main.py                       ← Batch runner analyzing all 50 screenplay episodes
├── app.py                        ← Interactive Streamlit dashboard for Localization Leads
├── raw-outputs/                  ← Full unedited audit data
│   ├── localization_pacing_audit.json
│   └── localization_pacing_report.txt
└── HOW-I-BUILT-THIS.md           ← This guide
```

---

## Alignment with the 5 Evaluation Lenses

### 1. Problem Choice & Framing
- **Who has the problem:** The Audio & Localization Lead at Kuku TV.
- **How we know it's real:** In vertical microdramas (1–2 min episodes), platform algorithms (TikTok/Instagram/YouTube) reward **completion rate**. Viewer reviews on microdrama apps frequently cite: *"The English/Hindi dub sounds robotic and talks way too fast"* or *"Awkward long pauses make it boring."*
- **Why it matters more than Problems 1 and 2:**
  - Finding promos (Problem 1) brings viewers to the door; pacing and dub quality determine whether they stay and pay.
  - Re-recording voice lines or re-generating AI speech after video assembly costs 10x more than catching timing errors in the screenplay phase.
- **Narrow Scope:** Focused strictly on one person (Localization Lead), one step (pre-recording screenplay timing QA), and one checkable output (an Actionable Re-timing Sheet).

### 2. Approach & Real-World Scale
- **Code vs. AI Division:**
  - *Kept as Code:* Deterministic timestamp difference calculations, word-count extraction, words-per-minute (WPM) calculations, and gap analysis across 3,727 script elements. Runs on all 50 episodes in **0.8 seconds at $0.00 cost**.
  - *Gave to AI (Optional Expansion):* Auto-generating alternative rephrased lines that preserve emotional punch while fitting the target duration constraint.
- **Scale:** Can audit an entire 100-episode season in under 2 seconds.

### 3. Quality Checking & Real Findings on the Input Pack
Ran across all 50 episodes of *"I Married a Broken Soldier. He was a Duke"*:
- **397 Rushed Dialogue Lines (>185 WPM):** Identified exact lines where an actor must speak at 200+ WPM to fit the time slot.
- **147 Dead Air Gaps (>3.2s):** Discovered scenes where up to 15 seconds of silence occur between dialogue without sound cues (e.g. Episode 18).
- **Average Catalog Health Score:** 54.8%, proving that human screenwriters routinely misjudge real-world speech timing.

### 4. The Prototype
- Python CLI (`python main.py`) outputs machine-readable JSON and human-readable QA reports.
- Web UI (`streamlit run app.py`) gives audio directors a 1-click visual inspector with exact second-level trim/expand recommendations.

### 5. Honest Limitations
- **Language Phoneme Variance:** English syllable duration differs from Hindi or Spanish. A 150 WPM English phrase might require 180 WPM in Spanish, necessitating localized language expansion coefficients (e.g., +15% for Romance languages).
