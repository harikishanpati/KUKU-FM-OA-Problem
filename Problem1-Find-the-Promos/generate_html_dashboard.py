"""
GENERATE STANDALONE HTML DASHBOARD
==================================
Builds a single-file, zero-dependency interactive HTML dashboard.
Can be opened by simply double-clicking in ANY web browser without running any server!
"""

import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(SCRIPT_DIR, "raw-outputs")

with open(os.path.join(RAW_DIR, "ranked_promos.json"), "r", encoding="utf-8") as f:
    ranked = json.load(f)

with open(os.path.join(RAW_DIR, "parsed_episodes.json"), "r", encoding="utf-8") as f:
    episodes = {e['episode_number']: e for e in json.load(f)}

with open(os.path.join(RAW_DIR, "quality_report.json"), "r", encoding="utf-8") as f:
    quality = json.load(f)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Kuku AI Microdrama Promo Studio</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #f8fafc; padding: 24px; }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    header {{ border-bottom: 1px solid #334155; padding-bottom: 16px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; }}
    h1 {{ font-size: 26px; color: #ef4444; font-weight: 800; }}
    .sub {{ color: #94a3b8; font-size: 14px; margin-top: 4px; }}
    .kpi-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }}
    .kpi-card {{ background: #1e293b; padding: 18px; border-radius: 8px; border: 1px solid #334155; }}
    .kpi-title {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; font-weight: 600; }}
    .kpi-val {{ font-size: 24px; font-weight: 700; color: #f8fafc; margin-top: 6px; }}
    .promo-card {{ background: #1e293b; border: 1px solid #334155; border-radius: 8px; margin-bottom: 20px; padding: 20px; transition: border-color 0.2s; }}
    .promo-card:hover {{ border-color: #ef4444; }}
    .promo-header {{ display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 12px; }}
    .rank-badge {{ background: #ef4444; color: white; padding: 4px 10px; border-radius: 4px; font-weight: 700; font-size: 13px; margin-right: 8px; }}
    .ep-title {{ font-size: 18px; font-weight: 600; color: #f8fafc; }}
    .time-badge {{ background: #334155; color: #cbd5e1; padding: 4px 8px; border-radius: 4px; font-size: 12px; }}
    .promo-grid {{ display: grid; grid-template-columns: 3fr 2fr; gap: 20px; }}
    .hook-box {{ background: #0f172a; border-left: 4px solid #f59e0b; padding: 12px; border-radius: 4px; margin-bottom: 10px; font-size: 14px; }}
    .cliff-box {{ background: #0f172a; border-left: 4px solid #ef4444; padding: 12px; border-radius: 4px; margin-bottom: 10px; font-size: 14px; }}
    .why-box {{ background: #0f172a; border-left: 4px solid #10b981; padding: 12px; border-radius: 4px; font-size: 14px; }}
    .metric-row {{ display: flex; justify-content: space-between; font-size: 12px; color: #94a3b8; margin-bottom: 4px; }}
    .progress-bar {{ background: #334155; height: 8px; border-radius: 4px; overflow: hidden; margin-bottom: 10px; }}
    .fill {{ height: 100%; border-radius: 4px; }}
    .fill-hook {{ background: #f59e0b; }}
    .fill-emo {{ background: #ef4444; }}
    .fill-conf {{ background: #8b5cf6; }}
    .fill-cliff {{ background: #ec4899; }}
    .fill-stand {{ background: #10b981; }}
    .script-snippet {{ margin-top: 14px; background: #0f172a; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 12px; line-height: 1.5; max-height: 180px; overflow-y: auto; }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <h1>🎬 Kuku AI Microdrama Promo Studio</h1>
        <div class="sub">Production Prototype: Automated Hook & Cliffhanger Extraction across 50 Episodes</div>
      </div>
      <div>
        <span style="background: #10b981; color: #042f2e; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 700;">● ZERO-DEPENDENCY LIVE DASHBOARD</span>
      </div>
    </header>

    <div class="kpi-row">
      <div class="kpi-card">
        <div class="kpi-title">Catalog Episodes</div>
        <div class="kpi-val">{len(episodes)}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Candidate Windows Scored</div>
        <div class="kpi-val">176</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Average Promo Duration</div>
        <div class="kpi-val">47.5s</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Top Hook Score</div>
        <div class="kpi-val">{ranked[0]['scores']['hook']} / 15</div>
      </div>
    </div>

    <h2 style="font-size: 18px; margin-bottom: 16px; color: #cbd5e1;">🔥 Top Diversified Social Promos (TikTok / Reels / Shorts)</h2>
"""

for p in ranked:
    ep = episodes.get(p['episode_number'], {})
    s = p['scores']
    
    # script snippet
    snippet_lines = []
    if ep and 'all_elements' in ep:
        matches = [el for el in ep['all_elements'] if el['end_time'] > p['start_time'] and el['start_time'] < p['end_time']]
        for el in matches[:6]:
            if el['type'] == 'DIALOGUE':
                snippet_lines.append(f"<span style='color: #38bdf8;'><b>{el['speaker']}:</b></span> \"{el['text']}\"")
            elif el['type'] == 'ACTION':
                snippet_lines.append(f"<span style='color: #94a3b8;'><i>[ACTION] {el['text'][:80]}...</i></span>")
    
    snippet_html = "<br>".join(snippet_lines)

    html_content += f"""
    <div class="promo-card">
      <div class="promo-header">
        <div>
          <span class="rank-badge">RANK #{p['rank']}</span>
          <span class="ep-title">Episode {p['episode_number']}</span>
        </div>
        <div>
          <span class="time-badge">⏱️ {p['start_ts']} ➔ {p['end_ts']} ({p['duration']}s)</span>
          <span class="time-badge" style="background: #10b981; color: black; font-weight: bold; margin-left: 6px;">Score: {p.get('rank_score', 0):.2f}</span>
        </div>
      </div>

      <p style="color: #94a3b8; font-size: 13px; margin-bottom: 14px;"><b>Logline:</b> {p.get('logline', 'N/A')}</p>

      <div class="promo-grid">
        <div>
          <div class="hook-box"><b>🪝 The 3-Second Hook:</b><br>{p.get('hook_text', 'N/A')}</div>
          <div class="cliff-box"><b>⏸️ The Cliffhanger Cut:</b><br>{p.get('cliffhanger_text', 'N/A')}</div>
          <div class="why-box"><b>💡 Why This Converts:</b><br>{p.get('why_it_works', 'High emotional stakes')}</div>
        </div>
        <div>
          <div class="metric-row"><span>Hook Strength</span><span>{s['hook']} / 15</span></div>
          <div class="progress-bar"><div class="fill fill-hook" style="width: {(s['hook']/15)*100}%;"></div></div>

          <div class="metric-row"><span>Emotional Charge</span><span>{s['emotion']} / 20</span></div>
          <div class="progress-bar"><div class="fill fill-emo" style="width: {(s['emotion']/20)*100}%;"></div></div>

          <div class="metric-row"><span>Conflict & Stakes</span><span>{s['conflict']} / 15</span></div>
          <div class="progress-bar"><div class="fill fill-conf" style="width: {(s['conflict']/15)*100}%;"></div></div>

          <div class="metric-row"><span>Cliffhanger Tension</span><span>{s['cliffhanger']} / 10</span></div>
          <div class="progress-bar"><div class="fill fill-cliff" style="width: {(s['cliffhanger']/10)*100}%;"></div></div>

          <div class="metric-row"><span>Standalone Clarity</span><span>{s['standalone']} / 10</span></div>
          <div class="progress-bar"><div class="fill fill-stand" style="width: {(s['standalone']/10)*100}%;"></div></div>
        </div>
      </div>

      <div class="script-snippet">
        <div style="color: #64748b; margin-bottom: 4px; font-weight: bold;">SCENE EXCERPT:</div>
        {snippet_html}
      </div>
    </div>
"""

html_content += """
  </div>
</body>
</html>
"""

out_html = os.path.join(SCRIPT_DIR, "dashboard.html")
with open(out_html, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ Standalone HTML Dashboard created at: {out_html}")
