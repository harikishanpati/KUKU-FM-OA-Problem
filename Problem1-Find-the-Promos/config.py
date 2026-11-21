"""
CONFIG — All tunable settings in one place.
============================================
Change these to adjust scoring weights, window sizes, model selection, etc.
During your interview, you can tweak these live to show how the tool adapts.
"""

# ─── MODEL SELECTION ────────────────────────────────────────────────
# Which scoring model to use. Options:
#   "heuristic"  → Fast keyword-based scoring (default, no API needed)
#   "gemini"     → Google Gemini API (free tier: gemini-2.0-flash)
#   "openai"     → OpenAI API (GPT-4o / GPT-4o-mini)
#   "hybrid"     → Heuristic pre-filter + LLM re-rank (best quality)
MODEL = "heuristic"

# ─── API KEYS (only needed if MODEL != "heuristic") ────────────────
# Set these here OR as environment variables:
#   export GEMINI_API_KEY="your-key"
#   export OPENAI_API_KEY="your-key"
GEMINI_API_KEY = ""       # or set env var GEMINI_API_KEY
OPENAI_API_KEY = ""       # or set env var OPENAI_API_KEY

# Which specific model name to use with each provider
GEMINI_MODEL_NAME = "gemini-2.0-flash"       # Free tier
OPENAI_MODEL_NAME = "gpt-4o-mini"            # Cheapest good model

# ─── SLIDING WINDOW SETTINGS ───────────────────────────────────────
MIN_PROMO_DURATION = 20   # Minimum promo length in seconds
MAX_PROMO_DURATION = 60   # Maximum promo length in seconds
WINDOW_STEP = 5           # Slide window by this many seconds each step
WINDOW_SIZES = [20, 30, 40, 50, 60]  # Window durations to try

# ─── SCORING WEIGHTS (for ranking) ─────────────────────────────────
# These control how much each criterion matters in the final ranking.
# They should sum to 1.0
WEIGHT_HOOK = 0.30         # First impressions matter most on social media
WEIGHT_EMOTION = 0.25      # Emotional content gets shared
WEIGHT_CONFLICT = 0.20     # Drama drives clicks
WEIGHT_CLIFFHANGER = 0.15  # Makes viewers download the app
WEIGHT_STANDALONE = 0.10   # Must make sense to new viewers

# ─── OUTPUT SETTINGS ───────────────────────────────────────────────
TOP_N_PROMOS = 20          # How many promos to include in final ranking
MAX_PER_EPISODE = 3        # Max promos per episode (for diversity)
OVERLAP_THRESHOLD = 0.5    # Remove candidates that overlap more than this

# ─── HOOK DETECTION ────────────────────────────────────────────────
HOOK_WINDOW_SECONDS = 3.0  # How many seconds at the start count as "hook"
CLIFFHANGER_TAIL_SECONDS = 5.0  # How many seconds at the end to check
