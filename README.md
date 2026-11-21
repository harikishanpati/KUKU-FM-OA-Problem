# Kuku — AI Generalist Assignment Solutions
Candidate Submission for **Kuku AI Generalist Role** (AI-Generated Microdrama).

---

## 📌 Repository Overview

This repository contains full, working production prototypes and evaluations for the **Kuku AI Generalist Assignment**, evaluated against the 5 core lenses:
1. **Problem choice and framing**
2. **Approach and scale**
3. **Quality checking & honest failure modes**
4. **The prototype** (runs on real inputs, produces actionable outputs)
5. **Communication** (clear, dense, decision-ready)

---

## 📂 Project Structure

```text
├── Problem1-Find-the-Promos/                    ← PRIMARY SUBMISSION
│   ├── main.py                                 ← Master CLI pipeline (runs in 1.1s)
│   ├── run_app.py                              ← Interactive Streamlit studio launcher
│   ├── dashboard.html                          ← Standalone zero-server browser dashboard
│   ├── config.py                               ← Hyperparameters & scoring weights
│   ├── models/                                 ← Swappable Model Layer (Heuristic, Gemini, OpenAI)
│   │   ├── base_model.py
│   │   ├── heuristic_model.py
│   │   ├── gemini_model.py
│   │   └── openai_model.py
│   ├── step1-parser/                           ← Regex screenplay parser
│   ├── step2-promo-finder/                     ← 20–60s sliding window & scoring
│   ├── step3-ranker/                           ← Weighted ranker & diversification
│   ├── step4-quality-check/                    ← Automated QA audit & failure report
│   ├── Solution_Doc_Kuku_AI_Generalist.pdf     ← Official 2-Page Solution Document
│   ├── WALKTHROUGH_SCRIPT.md                   ← 3-Minute screen recording script
│   └── raw-outputs/                            ← Full unedited 50-episode run outputs
│
├── Problem2-AI-Lawyer/                         ← PROBLEM 2: EVERYDAY INDIAN LEGAL HELPER
│   ├── ai_lawyer.py                            ← Case builder, options explainer, notice drafter
│   ├── main.py                                 ← Test suite across 5 realistic Indian disputes
│   ├── run_app.py                              ← Streamlit legal co-pilot UI
│   ├── knowledge_base/                         ← Grounded statutes (Zero hallucinations)
│   └── raw-outputs/                            ← Test case outputs & legal demand notices
│
├── Problem3-Microdrama-Localization-Auditor/   ← PROBLEM 3: LOCALIZATION PACING AUDITOR
│   ├── auditor/                                ← Speech velocity (WPM) & dead air (>3.2s) auditor
│   ├── main.py                                 ← 50-episode catalog audit runner
│   ├── run_app.py                              ← QA dashboard for Localization Leads
│   └── raw-outputs/                            ← 50-episode pacing defect audit logs
│
├── requirements.txt                            ← Python package dependencies
└── README.md                                   ← This documentation
```

---

## 🎬 Problem 1: Find the Promos (Quickstart)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Full Pipeline (1.1 seconds)
```bash
cd Problem1-Find-the-Promos
python main.py
```
Outputs the Top 20 ranked promo cuts across all 50 episodes with exact start/end timestamps, hook descriptions, and conversion rationales.

### 3. Launch the Interactive Editor Studio
```bash
python run_app.py
```
*(Or double-click `dashboard.html` for an instant zero-server browser experience).*

### 4. Swappable Model Support (Interview Scenario)
Run on new shows or switch model engines via CLI flags:
```bash
python main.py --input "path/to/new-show/" --model gemini --api-key "YOUR_KEY"
```

---

## ⚖️ Confidentiality Note
In strict accordance with the assignment brief (*"The input pack is Kuku's own content... please don't publish or share it"*), the raw proprietary screenplay folder has been excluded from this public repository via `.gitignore`. The code, models, reports, and generated outputs are fully open for review.
