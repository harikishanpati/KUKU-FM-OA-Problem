# Kuku — AI Generalist Assignment Solutions

**Candidate:** Harikishan Pati  
**Roll No:** 722MM1051  
**Branch:** Metallurgical and Materials Engineering  
**Repository:** [https://github.com/harikishanpati/KUKU-FM-OA-Problem](https://github.com/harikishanpati/KUKU-FM-OA-Problem)  

---

## 🌐 Live Interactive Prototypes (Streamlit Cloud)

All three assignment prototypes are live, interactive, and publicly accessible:

| Problem | Live Application Link | Focus Area |
| :--- | :--- | :--- |
| **Problem 1** | 🚀 [kuku-fm-oa-problem1.streamlit.app](https://kuku-fm-oa-problem1.streamlit.app/) | **Automated Promo Finder & Ranking Studio** (Hook-to-Cliffhanger detection for Reels & Shorts) |
| **Problem 2** | ⚖️ [kuku-fm-oa-problem2.streamlit.app](https://kuku-fm-oa-problem2.streamlit.app/) | **NyayaAI — Everyday Indian Legal Co-Pilot** (Rent, consumer, and wage dispute demand notices) |
| **Problem 3** | ⏱️ [kuku-fm-oa-problem-3.streamlit.app](https://kuku-fm-oa-problem-3.streamlit.app/) | **Microdrama Pacing & Localization Auditor** (Pre-recording QA for rushed speech & dead air) |

---

## 📑 Deliverables & Executive Documents

### 1. Two-Page Executive Solution PDFs (Times New Roman, Publication-Ready)
Each solution document strictly adheres to Kuku's $\le 2$-page constraint, written in plain, accessible English without academic jargon:
* 📄 **Problem 1:** [`Problem1-Find-the-Promos/Solution_Doc_Problem1.pdf`](Problem1-Find-the-Promos/Solution_Doc_Problem1.pdf) *(and official [`Solution_Doc_Kuku_AI_Generalist.pdf`](Problem1-Find-the-Promos/Solution_Doc_Kuku_AI_Generalist.pdf))*
* 📄 **Problem 2:** [`Problem2-AI-Lawyer/Solution_Doc_Problem2.pdf`](Problem2-AI-Lawyer/Solution_Doc_Problem2.pdf)
* 📄 **Problem 3:** [`Problem3-Microdrama-Localization-Auditor/Solution_Doc_Problem3.pdf`](Problem3-Microdrama-Localization-Auditor/Solution_Doc_Problem3.pdf)
* 🔄 **Recompile All PDFs:** Run `python generate_all_solution_pdfs.py` to regenerate all 4 PDFs at once.

### 2. Video Walkthrough Guide & Recording Scripts
* 🎥 **Guide & Scripts PDF:** [`Video_Walkthrough_Scripts_Guide.pdf`](Video_Walkthrough_Scripts_Guide.pdf)
  * Includes setup checklist, timing budget ($\le 3$ minutes), on-screen visual actions (`[ACTION: ...]`), and word-for-word spoken scripts for each problem as well as a combined 3-minute master script.
  * Recompile script: `python generate_video_script_pdf.py`

---

## 📂 Visual Repository Architecture

```text
KUKU-FM-OA-Problem/
├── Problem1-Find-the-Promos/                    ← PROBLEM 1: PROMO FINDER & RANKING STUDIO
│   ├── main.py                                 ← Master CLI pipeline runner
│   ├── config.py                               ← Global thresholds & scoring weights
│   ├── app.py / run_app.py / run_app.bat       ← Interactive Streamlit UI (Port 8501)
│   ├── dashboard.html                          ← Standalone zero-server browser dashboard
│   ├── step1-parser/screenplay_parser.py       ← 50-episode raw text parser
│   ├── step2-promo-finder/promo_finder.py      ← Sliding window & candidate scoring
│   ├── step3-ranker/promo_ranker.py            ← Weighted ranking & catalog diversification
│   ├── step4-quality-check/quality_checker.py  ← Quality audit & honest failure detection
│   ├── models/                                 ← Swappable model layer (Heuristic, Gemini, OpenAI)
│   ├── Solution_Doc_Problem1.pdf               ← Clean 2-page Executive Solution PDF
│   ├── Solution_Doc_Kuku_AI_Generalist.pdf     ← Official 2-page Solution PDF
│   ├── generate_solution_pdf.py                ← Problem 1 PDF generator
│   ├── WALKTHROUGH_SCRIPT.md                   ← Standalone markdown recording script
│   ├── HOW-I-BUILT-THIS.md                     ← Deep technical build notes
│   └── raw-outputs/                            ← JSON/TXT outputs from 50-episode audit
│
├── Problem2-AI-Lawyer/                         ← PROBLEM 2: NYAYAAI LEGAL CO-PILOT
│   ├── main.py                                 ← 5-case test suite runner
│   ├── ai_lawyer.py                            ← Grounded statutory engine
│   ├── app.py / run_app.py / run_app.bat       ← Interactive Streamlit UI (Port 8502)
│   ├── knowledge_base/legal_rules.json         ← Codified Indian statutes (TPA, CPA, Wages Act)
│   ├── test_cases/test_cases.json              ← 5 realistic Indian dispute scenarios
│   ├── Solution_Doc_Problem2.pdf               ← Clean 2-page Executive Solution PDF
│   ├── HOW-I-BUILT-THIS.md                     ← Deep technical build notes
│   └── raw-outputs/                            ← Generated demand notices and analysis logs
│
├── Problem3-Microdrama-Localization-Auditor/   ← PROBLEM 3: PACING & LOCALIZATION AUDITOR
│   ├── main.py                                 ← 50-episode catalog audit runner
│   ├── app.py / run_app.py / run_app.bat       ← Interactive Streamlit UI (Port 8503)
│   ├── auditor/pacing_auditor.py               ← WPM & Dead Air detection engine
│   ├── Solution_Doc_Problem3.pdf               ← Clean 2-page Executive Solution PDF
│   ├── HOW-I-BUILT-THIS.md                     ← Deep technical build notes
│   └── raw-outputs/                            ← Episode-level audit JSON and report
│
├── generate_all_solution_pdfs.py               ← Master compiler for all 3 solution PDFs
├── generate_video_script_pdf.py                ← Master compiler for video scripts PDF
├── Video_Walkthrough_Scripts_Guide.pdf         ← 5-page printable Video Walkthrough Guide
├── folder_struct.txt                           ← Visual folder map
├── requirements.txt                            ← Unified dependencies
└── README.md                                   ← Project documentation
```

---

## 🎬 Problem 1: Automated Promo Finder & Ranking Studio

### The Challenge
Kuku produces microdramas with 50+ 1-minute episodes per show. Video editors spend 4 to 6 hours per show manually reading scripts to find high-converting 30–50s promo cuts for TikTok, Instagram Reels, and YouTube Shorts.

### Our Solution
A production-grade algorithmic pipeline that parses raw screenplay scripts, slides 20–60s temporal windows, scores viral potential using an empirical retention formula, and diversifies the catalog so no single episode dominates.

* **Retention Scoring Formula (0 to 100):**
  $$\text{Score} = 0.30 \cdot \text{Hook} + 0.25 \cdot \text{Emotion} + 0.20 \cdot \text{Conflict} + 0.15 \cdot \text{Cliffhanger} + 0.10 \cdot \text{Clarity}$$
* **Swappable Architecture:** Supports 100% offline rule heuristics ($0.00 cost, 1.5s runtime), Google Gemini Flash API, OpenAI GPT-4o-mini, and Hybrid Mode.
* **Catalog Safeguards:** Enforces natural dialogue boundaries (never cuts mid-sentence) and max 2 promos per episode (selected across 17 distinct episodes).

### Quickstart (Problem 1)
```bash
# 1. Run full CLI pipeline across all 50 episodes (1.5 seconds)
cd Problem1-Find-the-Promos
python main.py

# 2. Launch interactive Streamlit Studio
python run_app.py
```

---

## ⚖️ Problem 2: NyayaAI — Everyday Indian Legal Co-Pilot

### The Challenge
Millions of Indians face rent deposit extortion (Rs. 30,000 to Rs. 80,000), e-commerce refund denials, and unpaid wages. Hiring a lawyer costs Rs. 15,000 to Rs. 50,000—economically unfeasible for disputes under Rs. 1 Lakh.

### Our Solution
A grounded legal co-pilot that accepts conversational stories in English or Hinglish, maps them to real codified Indian statutes, drafts formal 15-day Legal Demand Notices, and enforces strict ethical escalation.

* **Zero Hallucinated Laws:** Strictly quotes codified acts:
  * **Rent Deposits:** Section 108 of the Transfer of Property Act 1882 (prohibits deductions for normal wear & tear).
  * **Damaged Deliveries:** Consumer Protection Act 2019 (unfair trade practices & e-Daakhil filing).
  * **Unpaid Salaries:** Payment of Wages Act 1936 (prohibits unauthorized wage retention).
* **Ethical Safety Gate:** If criminal threats, blackmail, or recovery agent police arrest intimidation are detected, the tool **immediately halts civil notice generation**, triggers a critical warning under IPC Section 384 (Extortion), and routes the citizen to the National Cybercrime Helpline (1930).
* **Speed & Economics:** Audits statutory rules in **0.2 seconds** at **Zero Cost ($0.00)**.

### Quickstart (Problem 2)
```bash
# 1. Run test suite across 5 realistic Indian dispute cases
cd Problem2-AI-Lawyer
python main.py

# 2. Launch interactive Streamlit Legal Assistant
python run_app.py
```

---

## ⏱️ Problem 3: Microdrama Pacing & Localization Auditor

### The Challenge
In vertical short-form drama, retention is 90% driven by audio pacing. Dialogue rushed above 185 WPM sounds robotic and causes AI voice models (ElevenLabs) to clip words. Conversely, silent gaps longer than 3.2 seconds trigger mobile viewers to swipe away. Re-recording voice actors post-production costs 10× more than script QA.

### Our Solution
An automated pre-recording script auditor that ingests screenplay timestamps `(MM:SS.SS)`, calculates speaking speed (WPM) per dialogue line, and identifies retention-killing dead air.

* **Auditor Guardrails:**
  * **Normal Dialogue Cadence:** 110 to 165 WPM.
  * **RUSH Warning Threshold:** $>185\text{ WPM}$ (requires word trimming or duration extension).
  * **DRAG Warning Threshold:** $<65\text{ WPM}$ (unintentional sluggish dialogue).
  * **Dead Air Retention Cliff:** $>3.2\text{ seconds}$ unexplained silence without sound effects.
* **Findings on Kuku's 50 Episodes (3,727 elements, 1,487 dialogue lines):**
  * Average Catalog Health Score: **54.8%** (scores ranged from 0% in Ep 9/11 to 94% in Ep 42).
  * Rushed Dialogue Lines: **397 lines** (e.g., Ep 1 Lady Juliana at 245 WPM in 2.2s).
  * Retention Dead Air Gaps: **147 pauses** (e.g., Ep 1 8.3s dead silence before dialogue).
* **Actionable Math Remediation:**
  $$\text{Target Seconds} = \frac{\text{Word Count}}{150} \times 60 \qquad\Big|\qquad \text{Words to Delete} = \text{Word Count} - \left(\frac{150 \times \text{Seconds}}{60}\right)$$

### Quickstart (Problem 3)
```bash
# 1. Run catalog audit on all 50 episodes (0.8 seconds)
cd Problem3-Microdrama-Localization-Auditor
python main.py

# 2. Launch interactive Streamlit Auditor Studio
python run_app.py
```

---

## 💻 Local Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/harikishanpati/KUKU-FM-OA-Problem.git
cd KUKU-FM-OA-Problem
```

### 2. Set Up Virtual Environment & Dependencies
```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# Install unified requirements
pip install -r requirements.txt
```

### 3. Run Any Application
Each problem has a dedicated `run_app.py` script that automatically launches Streamlit in your default browser:
```bash
# Problem 1 Studio (Default port 8501)
python Problem1-Find-the-Promos/run_app.py

# Problem 2 Legal Co-Pilot (Default port 8502)
python Problem2-AI-Lawyer/run_app.py

# Problem 3 Localization Auditor (Default port 8503)
python Problem3-Microdrama-Localization-Auditor/run_app.py
```

---

## 🎯 Alignment with Kuku's 5 Evaluation Lenses

| Lens | How This Repository Demonstrates It |
| :--- | :--- |
| **1. Problem Choice & Framing** | Framed around vertical video economics: attention drop-off in the first 3s (P1), high legal fee barrier for small disputes (P2), and post-production re-recording costs driven by script pacing (P3). |
| **2. Approach & Scale** | Sub-second heuristic baselines ($0 cost) swappable with LLM semantic layers. Processes 50-episode seasons in under 2 seconds; horizontally scalable to hundreds of concurrent shows. |
| **3. Quality & Honest Failure Modes** | Transparently documents edge cases: text-only parsers cannot see visual acting chemistry or quiet cliffhangers; state-specific rent variations in India; and multi-lingual syllable expansion in Hindi/Spanish dubbing. |
| **4. Working Prototypes** | Built on real screenplay data (3,727 elements). Live Streamlit web apps and zero-server HTML dashboards produce actionable outputs (top cuts, formal demand letters, pacing fix formulas). |
| **5. Communication** | Concise 2-page publication-ready PDFs, structured video walkthrough scripts with second-by-second timestamps, and complete developer documentation. |

---

## ⚖️ Confidentiality & Data Note
In strict accordance with the assignment brief (*"The input pack is Kuku's own content... please don't publish or share it"*), the raw proprietary screenplay folder has been excluded from the public repository via `.gitignore`. All parsers, engines, test cases, and generated output reports run reliably out-of-the-box.
