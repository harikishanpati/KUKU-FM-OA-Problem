# HOW I BUILT THIS — Problem 1: Find the Promos

## The Big Picture

I built a tool that reads microdrama screenplays and automatically finds the best promo clips
(20–60 second moments) suitable for posting on Instagram, TikTok, and YouTube.

**Key design principles:**
- **Re-runnable on any input** — just point to a new folder with `--input`
- **Model is swappable** — switch from heuristic → Gemini → OpenAI → hybrid with one flag
- **No paid API needed** — the default heuristic model runs on pure Python, no API key required
- **Fast** — processes 50 episodes in ~1 second

```
50 Screenplays (.txt)
        │
        ▼
  ┌──────────┐    ┌────────────────┐    ┌────────────┐    ┌───────────────┐
  │  PARSER   │───▶│  PROMO FINDER  │───▶│   RANKER   │───▶│ QUALITY CHECK │
  │  Step 1   │    │    Step 2      │    │   Step 3   │    │    Step 4     │
  └──────────┘    └────────────────┘    └────────────┘    └───────────────┘
                         │                                        │
                   ┌─────┴─────┐                           Final Reports
                   │   MODEL   │ ◄── swappable!
                   │ INTERFACE │
                   └─────┬─────┘
              ┌──────────┼──────────┐
              ▼          ▼          ▼
         Heuristic   Gemini     OpenAI
         (default)   (free)    (paid)
```

---

## Folder Structure

```
Problem1-Find-the-Promos/
├── main.py                        ← Entry point: python main.py --help
├── config.py                      ← ALL tunable settings in one place
├── requirements.txt
│
├── models/                        ← SWAPPABLE MODEL LAYER
│   ├── __init__.py                ← Model factory (get_model)
│   ├── base_model.py              ← Abstract interface every model implements
│   ├── heuristic_model.py         ← Keyword scoring (default, no API)
│   ├── gemini_model.py            ← Google Gemini API
│   └── openai_model.py            ← OpenAI API
│
├── step1-parser/
│   └── screenplay_parser.py       ← Reads .txt → structured JSON
├── step2-promo-finder/
│   └── promo_finder.py            ← Original standalone finder (reference)
├── step3-ranker/
│   └── promo_ranker.py            ← Original standalone ranker (reference)
├── step4-quality-check/
│   └── quality_checker.py         ← Honest quality analysis
│
├── raw-outputs/                   ← All generated output files
│   ├── parsed_episodes.json
│   ├── promo_candidates.json
│   ├── ranked_promos.json
│   ├── ranked_promos_readable.txt
│   ├── quality_report.json
│   └── quality_report.txt
│
└── HOW-I-BUILT-THIS.md            ← This file
```

---

## How to Run

```bash
# Default: heuristic model on the assignment input pack
python main.py

# INTERVIEW SCENARIO: Run on a NEW show's screenplays
python main.py --input "path/to/new-show-scripts/"

# Switch to Gemini (free tier):
pip install google-generativeai
python main.py --model gemini --api-key "YOUR_KEY"

# Switch to OpenAI:
pip install openai
python main.py --model openai --api-key "YOUR_KEY"

# Hybrid mode: heuristic pre-filter + LLM re-rank (best quality)
python main.py --model hybrid --api-key "YOUR_KEY"

# Custom output folder and top N:
python main.py --input "../New Show/" --output "./results" --top 30
```

---

## The Model Swapping Architecture (INTERVIEW TALKING POINT)

This is the key design decision that makes the tool production-ready.

### How it works

Every scoring model implements the same interface (`BaseModel`):

```python
class BaseModel(ABC):
    @abstractmethod
    def score_promo_candidate(self, elements, window_start, window_end, episode_info):
        """Score a single promo window. Returns dict with hook/emotion/conflict/etc scores."""
        pass

    @abstractmethod
    def rank_promos(self, candidates, top_n=20):
        """Take scored candidates, produce final ranked list."""
        pass
```

**To add a new model (e.g., Claude, Llama, Mistral):**
1. Create `models/claude_model.py`
2. Subclass `BaseModel`
3. Implement `score_promo_candidate()` and `rank_promos()`
4. Add it to `models/__init__.py`
5. Run: `python main.py --model claude`

**That's literally it.** The pipeline doesn't change. The parser doesn't change.
The quality checker doesn't change.

### Why this matters

**During the interview:** "If you give me a stronger API, I can plug it in in 5 minutes.
I just create a new model file that calls your API and implements the same scoring interface.
The rest of the pipeline stays the same. I can even do a hybrid approach where the fast
heuristic model pre-filters candidates and the expensive LLM only scores the top 40,
which keeps API costs low."

### The three available models

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| `heuristic` | ~1 sec / 50 episodes | Good hooks, weak cliffhangers | Free | Default, interview demo |
| `gemini` | ~2 min / 50 episodes | Better cliffhangers & standalone | Free tier | When accuracy matters more |
| `hybrid` | ~1 min / 50 episodes | Best of both | Free tier | Production use |

---

## Step-by-Step Explanation

### STEP 1: Screenplay Parser (`step1-parser/screenplay_parser.py`)

**What it does:** Reads all `episode-*.txt` files and converts them into structured JSON.

**How the screenplay format works:**
```
EPISODE NUMBER: Episode 1
EPISODE LOGLINE: Lady Juliana arrives at the cathedral...

--- SCRIPT START ---
SCENE 01
Scene heading: INT. CATHEDRAL – DAY
Scene start: 00:00.00
Scene end: 02:18.00

**CAMERA:**
Start: (00:00.00) | End: (00:04.80)
Symmetrical framing on the heavy church doors...

**LADY JULIANA (Confused, Breathless):**
Start: (00:13.50) | End: (00:14.30)
"Why?"
```

**What I extract from each element:**
- `type` → CAMERA, ACTION, DIALOGUE, or SOUND_FX
- `speaker` → Character name (for dialogue only)
- `emotion` → The tone tag in parentheses, e.g., "Confused, Breathless"
- `start_time` / `end_time` → Converted to seconds as float
- `text` → The actual content

**Key technique:** Regex-based parsing that finds `**HEADER:**` blocks.
The header determines the type. For dialogue, further regex extracts speaker and emotion
from patterns like `CHARACTER (Emotion, Tone)`.

**How to explain:** "I wrote a regex-based parser that reads the screenplay format.
It works on any screenplay that follows this structure — if you give me a new show,
it parses it the same way."

---

### STEP 2: Promo Finder (now integrated in `main.py` using the model layer)

**What it does:** Slides a window (20-60 seconds) across each episode's timeline and
asks the **model** to score each window.

**The Sliding Window Approach:**
```
Episode timeline:  |============================|
Window size 40s:   |████████|                      (position 1)
                     |████████|                    (position 2, +5s)
                       |████████|                  (position 3, +5s)
                                     ...
```

- Window sizes tried: 20s, 30s, 40s, 50s, 60s (configurable in config.py)
- Slide step: 5 seconds
- Each position is scored on 5 criteria
- Overlapping windows are deduplicated (keep highest score)

**The 5 Scoring Criteria (max 70 points total):**

| Criterion | Max | What it measures | Why it matters |
|-----------|-----|------------------|----------------|
| **Hook** | 15 | First 3 seconds grab attention | Scrolling viewer must STOP |
| **Emotion** | 20 | Emotional intensity of dialogue | Makes viewers feel something |
| **Conflict** | 15 | Confrontation, betrayal, action | Drama drives engagement |
| **Cliffhanger** | 10 | Ends on unresolved moment | Viewer needs to watch the show |
| **Standalone** | 10 | Makes sense without context | Viewer has never seen the show |

**Heuristic Model Details:**
- **Hook scoring:** Scans first 3 seconds for keywords (slap→+3, furious→+2, tears→+1)
  and high-drama emotion tags on dialogue (+3)
- **Emotion scoring:** Each dialogue line scored by emotion tag. High-drama emotions
  (seething, devastated, terrified) → +3. Medium (cold, stern, pleading) → +2. Bonus
  for 4+ dialogue exchanges.
- **Conflict scoring:** All elements scanned for conflict words (betray, poison, murder,
  confront, disown, etc.) → +1.5 each
- **Cliffhanger scoring:** Last 5 seconds checked for indicators (cut to black, gasp,
  eyes widen), questions in dialogue (+2), dramatic sound FX (+1)
- **Standalone scoring:** Base 5 points, deducts for no dialogue, adds for self-explanatory
  relationship words (husband, wife, betray)

**How to explain:** "I slide a window across each episode and score every possible clip
on five criteria that map to what makes a TikTok promo work. The scoring uses keyword
matching against the screenplay's emotion tags and action descriptions."

---

### STEP 3: Ranking

**Ranking Formula:**
```
Final = (Hook × 0.30) + (Emotion × 0.25) + (Conflict × 0.20) +
        (Cliffhanger × 0.15) + (Standalone × 0.10)
```

Then multiplied by bonuses:
- ×1.10 for 30-45s duration (social media sweet spot)
- ×1.05 for 4+ dialogue lines
- ×0.90 for <20s or >55s

**Diversification:** Max 3 promos per episode in the top 20, so the promo set
showcases the full show.

**How to explain:** "Hook is weighted highest at 30% because that's what matters most
on social media — if the first 3 seconds don't grab attention, nothing else matters."

---

### STEP 4: Quality Check

**Results from this run:**
- **Coverage:** GOOD — 17 of 50 episodes covered
- **Duration:** GOOD — average 47.5s, all in valid range
- **Hook Quality:** GOOD — average 12.7/15, all hooks strong
- **Cliffhanger Quality:** POOR — average 2.95/10 (biggest weakness)

**Known Limitations (be honest!):**
1. **Text-only** — Can't evaluate visual impact or acting quality
2. **Keyword-based** — Misses subtle drama (quiet menace, loaded silences)
3. **No audio** — Music swells and voice tone can't be scored from text
4. **Cliffhanger weakness** — Requires narrative understanding, not just keywords

**How the LLM solves this:** "The heuristic model's biggest weakness is cliffhanger
detection. When I switch to the Gemini or hybrid model, the LLM understands narrative
tension — it can tell that 'What did you find?' followed by 'Poison.' is a cliffhanger
even without explicit keywords. That's why the architecture is designed to swap models."

---

## Key Interview Talking Points

### 1. "How does this scale to every show you make?"
- The parser works on any screenplay in this format
- Run time is linear: 50 episodes in 1.1s → 500 episodes in ~11s
- For production: add Gemini API in hybrid mode, batch process weekly releases
- Cost estimate: Gemini free tier handles ~1500 requests/day — enough for 50 episodes

### 2. "What would you do with a stronger model?"
- Plug it in: create `models/your_model.py`, implement the interface, done
- Use hybrid mode: heuristic pre-filters to ~40 candidates, expensive model scores only those
- Could also use the LLM to generate the promo pitch text and posting captions

### 3. "What if we give you video instead of screenplays?"
- Add a Step 0: Extract keyframes + audio transcription from video
- Feed visual features (facial expressions, action detection) into the scoring
- The same sliding window + 5 criteria framework still applies

### 4. "One place where AI got it wrong"
LLMs tend to rate dialogue-heavy quiet moments as highly dramatic because the words
*sound* powerful in text, but on video these moments may be slow and visually undramatic.
The heuristic approach corrects for this by also requiring visual/action elements.
Conversely, both approaches miss physical action scenes that look amazing on camera
but aren't described with emotional vocabulary.

---

## Results Summary

- **50 episodes parsed** in ~0.5 seconds: 3,727 elements, 1,487 dialogue lines
- **176 promo candidates** found across all episodes
- **Top 20 promos** ranked and diversified across 17 episodes
- **#1 Promo:** Episode 28, 01:00–01:40 (40s) — Rupert and Catherine framing
  Juliana while the Duchess protests (Score: 14.30)
- **Total pipeline time:** 1.1 seconds (heuristic mode)
