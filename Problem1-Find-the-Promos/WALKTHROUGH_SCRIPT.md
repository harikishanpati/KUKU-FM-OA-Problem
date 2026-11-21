# 🎬 3-Minute Walkthrough Video Script
**Assignment:** Kuku — AI Generalist Assignment  
**Problem:** Problem 1 — Find the Promos (Ads)  
**Speaker:** You (Candidate)  
**Target Time:** 2 minutes 45 seconds (Under the 3-minute hard limit)

---

### **[0:00 - 0:30] Introduction & Problem Framing**
*(Screen: Show `main.py` and the 50 episode files in VS Code / Terminal)*

> "Hi everyone, thank you for reviewing my submission for the Kuku AI Generalist assignment. Today I’m walking you through my solution for **Problem 1: Find the Promos**.
>
> In microdrama apps like ReelShort and Kuku, user acquisition lives or dies on viral social clips on TikTok and Instagram. Right now, human editors spend 4 to 6 hours watching 50 episodes to manually spot 20-to-60 second promo moments. That’s a massive bottleneck when you're releasing new shows every week.
>
> My goal was to build a tool that reads raw screenplays, detects high-converting promo moments automatically, and ranks them for immediate posting—cutting that editor review time from 5 hours to under 5 minutes."

---

### **[0:30 - 1:15] Architecture & Live Run**
*(Screen: Open terminal, run `python main.py`, show terminal output scrolling in 1 second)*

> "Let's run it live right now. I execute `python main.py`.
>
> *(Point cursor at the terminal)*  
> In just **1.1 seconds**, the pipeline processed all 50 full screenplays—that’s over 3,700 scene elements and 1,400 lines of dialogue. It generated 176 unique candidate windows and produced a diversified Top 20 ranked list.
>
> Here’s how the architecture works under the hood:
> 1. **Step 1 (Deterministic Parsing):** Code handles what code is best at—fast regex extraction of scene boundaries, timestamps, dialogue, and emotion tags.
> 2. **Step 2 (Sliding Window & 5-Metric Scoring):** We slide 20-to-60 second windows with a 5-second step. Every window is evaluated on five key criteria:
>    - The **3-second Hook** (stop scrolling),
>    - **Emotional intensity**,
>    - **Conflict and stakes**,
>    - An unresolved **Cliffhanger cut**,
>    - And **Standalone clarity** for a brand new viewer.
> 3. **Step 3 (Ranking & Diversification):** We apply a weighted formula with duration bonuses for the 30-to-45 second sweet spot, and enforce diversity caps so one episode doesn't monopolize the ads."

---

### **[1:15 - 2:00] Model Swappability & Streamlit UI**
*(Screen: Switch to the Streamlit app `streamlit run app.py` in browser)*

> "Now, one critical requirement from the brief was: **'Build something you can run again on new inputs, where models are easy to swap.'**
>
> Notice my model design in `config.py` and the `models/` directory. All models inherit from a clean `BaseModel` class. Today it runs with `heuristic`—which is 100% offline, deterministic, and free. But in our interview, if you provide a Gemini or OpenAI API key, I can switch to `--model gemini` or `--model hybrid` with zero code changes.
>
> *(In Streamlit UI, launched with `python -m streamlit run app.py`, expand Rank #1 - Episode 28)*  
> Here in our editor dashboard, look at our **#1 Ranked Promo** from Episode 28:
> - **Timestamps:** 01:00 to 01:40 (40 seconds).
> - **The Hook:** Rupert leaning menacingly over the bedridden Duchess.
> - **The Cliffhanger:** Juliana freezing in the doorway as she catches Catherine holding her mother's book.
> - **Why it works:** It's a classic high-stakes betrayal that creates an irresistible curiosity gap."

---

### **[2:00 - 2:45] Quality Checking, Honest Failures & Posting Strategy**
*(Screen: Switch to Tab 2 'Quality & Failure Analysis' in Streamlit or show `quality_report.txt`)*

> "Finally, let's talk about **Quality Checking and honest failure modes**:
>
> Across all 50 episodes, our tool achieves strong duration control—averaging 47.5 seconds—and 100% of our top promos have verified high-impact hooks.
>
> But being honest about limitations is part of the job:
> 1. **Text Blindness:** Screenplay directions cannot measure physical actor chemistry or micro-expressions without video multimodal analysis.
> 2. **Subtle Cliffhangers:** Code-based regex captures explicit questions and cuts to black easily, but subtle non-verbal psychological tension scored lower (average 2.9/10). That’s exactly where our swappable hybrid LLM layer shines—it reads narrative tension that keyword matching misses.
> 3. **Where AI got it wrong:** When testing pure zero-shot LLMs, they frequently favored lengthy poetic dialogue that reads well on paper but lacks the visual velocity needed for TikTok vertical video pacing.
>
> **Posting Strategy:** We post Ranks 1 to 5 first for cold user acquisition—pure shock hooks to minimize cost per install. Ranks 6 to 10 follow to build narrative intrigue and drive shares, and Ranks 11 to 20 sustain retargeting.
>
> Thank you, and I look forward to running this on a new show during our interview!"
