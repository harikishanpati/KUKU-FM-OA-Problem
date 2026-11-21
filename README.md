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

## 📂 Visual Folder Architecture

```text
Problem1-Find-the-Promos/
│
├── ⚙️ Orchestration & Config
│   ├── main.py                     ← Master CLI pipeline runner (parses, finds, ranks, audits)
│   ├── config.py                   ← Global settings, scoring weights & duration thresholds
│   └── requirements.txt            ← Installed Python package list
│
├── 🖥️ User Interface & Dashboard
│   ├── app.py                      ← Streamlit interactive UI application
│   ├── run_app.py                  ← Safe Python launcher for Streamlit (no errors)
│   ├── run_app.bat                 ← 1-click Windows desktop batch launcher
│   └── dashboard.html              ← Standalone zero-server browser dashboard
│
├── 🧩 The 4 Pipeline Steps
│   ├── step1-parser/
│   │   └── screenplay_parser.py    ← Parses raw .txt into structured JSON
│   ├── step2-promo-finder/
│   │   └── promo_finder.py         ← Sliding window & candidate scoring
│   ├── step3-ranker/
│   │   └── promo_ranker.py         ← Weighted ranking & catalog diversification
│   └── step4-quality-check/
│       └── quality_checker.py      ← Quality audit & honest failure detection
│
├── 🤖 Swappable Model Layer
│   └── models/
│       ├── __init__.py             ← Model factory (get_model)
│       ├── base_model.py           ← Abstract base class interface
│       ├── heuristic_model.py      ← 100% offline rule-based scoring (Default)
│       ├── gemini_model.py         ← Google Gemini Flash API integration
│       └── openai_model.py         ← OpenAI GPT-4o-mini API integration
│
├── 📊 Outputs & Deliverables
│   ├── Solution_Doc_Kuku_AI_Generalist.pdf  ← 2-Page Executive PDF for form
│   ├── generate_solution_pdf.py             ← Script that compiles the PDF
│   ├── generate_html_dashboard.py           ← Script that compiles dashboard.html
│   ├── WALKTHROUGH_SCRIPT.md                ← 3-minute video recording script
│   ├── HOW-I-BUILT-THIS.md                  ← Comprehensive technical notes
│   └── raw-outputs/
│       ├── parsed_episodes.json             ← 3,727 parsed screenplay elements
│       ├── promo_candidates.json            ← 176 scored candidate windows
│       ├── ranked_promos.json               ← Top 20 ranked promo cuts (JSON)
│       ├── ranked_promos_readable.txt       ← Human-readable promo report
│       ├── quality_report.json              ← Quantitative audit metrics
│       └── quality_report.txt               ← Transparent failure analysis
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
