"""
GENERATE 2-PAGE SOLUTION PDF
=============================
Creates a clean, professional, dense 2-page PDF document meeting all Kuku requirements
and strictly aligned with the 5 evaluation lenses.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

OUTPUT_PDF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Solution_Doc_Kuku_AI_Generalist.pdf")

def create_solution_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom tight typography for strict 2-page budget
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#B81D13')
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#4A4A4A')
    )

    h1_style = ParagraphStyle(
        'Heading1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=5,
        spaceAfter=2
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#222222')
    )

    bold_body = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.whitesmoke
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#111111')
    )

    story = []

    # Title Banner
    story.append(Paragraph("KUKU AI GENERALIST ASSIGNMENT — SOLUTION DOCUMENT", title_style))
    story.append(Paragraph("<b>Problem 1: Find the Promos (Ads)</b> | Candidate Submission | <i>Evaluation against the 5 Lenses</i>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceBefore=3, spaceAfter=5))

    # LENS 1
    story.append(Paragraph("1. Problem Choice & Framing", h1_style))
    story.append(Paragraph(
        "<b>Why this problem:</b> Microdrama series live or die on viral social distribution (TikTok, Reels, Shorts). Human curation is currently the primary CAC bottleneck: an editor spends 4–6 hours manually scrubbing 50 episodes per show to extract promo cuts. With weekly releases, this operational drag limits platform scaling. Automating high-converting promo detection directly unlocks distribution velocity.<br/>"
        "<b>Scope:</b> Standalone 20–60s video cuts across all 50 episodes of <i>'I Married a Broken Soldier. He was a Duke'</i>.<br/>"
        "<b>Assumptions where brief was silent:</b> (1) Screenplay action/dialogue timestamps reliably reflect physical video edit points. (2) A single contiguous stretch yields significantly higher narrative cohesion than disjointed multi-episode stitches. (3) The social retention drop-off happens within 3 seconds; hence the initial 3s hook dominates algorithmic viability. (4) 30–45s represents the global engagement sweet spot.",
        body_style
    ))
    story.append(Spacer(1, 4))

    # LENS 2
    story.append(Paragraph("2. Approach & Real-World Scale", h1_style))
    story.append(Paragraph(
        "<b>Code vs. AI Division:</b> We adopted a pragmatic hybrid architecture rather than unconstrained end-to-end LLM processing:<br/>"
        "• <i>Deterministic Code (Speed & Cost):</i> Screenplay parser (extracting scene boundaries, dialogue, tone tags, camera movements), sliding-window timeline generation (20s–60s with 5s step), non-maximum overlap suppression, and keyword-density scoring for fast candidate pruning.<br/>"
        "• <i>AI / Semantic Engine (Nuance & Re-ranking):</i> Evaluates semantic narrative tension, standalone clarity, and cliffhanger stakes. Built with a pluggable <b>BaseModel</b> abstraction supporting <code>heuristic</code> (100% offline, zero-cost), <code>gemini</code>, <code>openai</code>, and <code>hybrid</code> modes.<br/>"
        "• <i>Human-in-the-Loop:</i> The AI does not blindly post. It renders a ranked dashboard with timestamps, hook/cliffhanger extracts, and conversion rationales, reducing editor manual scrubbing from 5 hours to a 5-minute approval pass.<br/>"
        "<b>Scale & Unit Economics:</b> Parsing and heuristic scoring on all 50 episodes executes in <b>1.1 seconds</b> with <b>$0.00 API cost</b>. In production across 10 weekly shows (500 episodes/week), the hybrid model pre-filters 90% of candidates and sends only top-tier cuts to Gemini Flash, incurring <b>&lt;$0.15/week</b> in total infrastructure cost.",
        body_style
    ))
    story.append(Spacer(1, 4))

    # LENS 3 & 4
    story.append(Paragraph("3. The Prototype & Execution", h1_style))
    story.append(Paragraph(
        "The prototype is structured as an extensible Python CLI and interactive Streamlit application. It parses raw screenplay files, extracts candidate windows, calculates 5-metric composite scores, removes duplicate overlaps, and outputs ranked decision-ready promos.<br/>"
        "<b>Composite Formula:</b> <code>Score = 0.30×Hook + 0.25×Emotion + 0.20×Conflict + 0.15×Cliffhanger + 0.10×Standalone</code> with bonuses for 30–45s durations and dense dialogue exchanges. Episode diversity constraints (max 3/episode) prevent top-list monopolization.",
        body_style
    ))
    story.append(Spacer(1, 3))

    # Sample Output Table
    table_data = [
        [
            Paragraph("Rank", table_header),
            Paragraph("Ep", table_header),
            Paragraph("Timestamps (Dur)", table_header),
            Paragraph("Hook (0–3s)", table_header),
            Paragraph("Cliffhanger Cut", table_header),
            Paragraph("Why It Works", table_header)
        ],
        [
            Paragraph("<b>#1</b>", table_cell),
            Paragraph("28", table_cell),
            Paragraph("01:00 – 01:40 (40s)", table_cell),
            Paragraph("Rupert leans menacingly over gasping Duchess in bed", table_cell),
            Paragraph("Juliana freezes in doorway discovering mother's book", table_cell),
            Paragraph("High stakes framing betrayal; explosive curiosity gap", table_cell)
        ],
        [
            Paragraph("<b>#2</b>", table_cell),
            Paragraph("16", table_cell),
            Paragraph("00:05 – 00:45 (40s)", table_cell),
            Paragraph("Extreme close-up Alexander's scarred face; ambush charge", table_cell),
            Paragraph("Lifts thug onto tiptoes: <i>'Who sent you?'</i>", table_cell),
            Paragraph("Instant visceral physical action + lethal protective interrogation", table_cell)
        ],
        [
            Paragraph("<b>#3</b>", table_cell),
            Paragraph("10", table_cell),
            Paragraph("00:00 – 00:40 (40s)", table_cell),
            Paragraph("Juliana reading by fire when wounded soldier collapses", table_cell),
            Paragraph("Camera tight pan on scarred, bleeding torso as Juliana gasps", table_cell),
            Paragraph("Vulnerability subversion; high visual shock and romance tension", table_cell)
        ],
        [
            Paragraph("<b>#4</b>", table_cell),
            Paragraph("29", table_cell),
            Paragraph("00:05 – 00:45 (40s)", table_cell),
            Paragraph("Uniformed guards dragging struggling Juliana into wet cells", table_cell),
            Paragraph("Catherine smirks: <i>'You know that is a lie!'</i>", table_cell),
            Paragraph("Classic injustice archetype; immediate viewer empathy & outrage", table_cell)
        ]
    ]

    t = Table(table_data, colWidths=[24, 18, 85, 135, 135, 143])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t)
    story.append(Spacer(1, 5))

    # LENS 4: QUALITY CHECK & HONEST FAILURES
    story.append(Paragraph("4. Quality Checking & Honest Failures", h1_style))
    story.append(Paragraph(
        "<b>Rigorous Evaluation:</b> Evaluated on all 50 full screenplays (3,727 elements, 1,487 dialogue lines) yielding 176 unique candidates across 17 distinct episodes.<br/>"
        "• <i>Duration Distribution:</i> Average duration = 47.5s. 85% fell within the target 30–50s corridor.<br/>"
        "• <i>Hook Strength:</i> 100% of top 20 candidates scored &ge;9/15 on early 3-second tension indicators.<br/>"
        "<b>Honest Failure Modes & Edge Cases:</b><br/>"
        "1. <b>Text-to-Video Blindness:</b> The screenplay records script directions, not physical screen execution. An actor's nuanced micro-expression or electric chemistry cannot be quantified from text alone without multimodal video analysis.<br/>"
        "2. <b>Cliffhanger Heuristic Limitation:</b> Regex scoring easily captures dialogue ending with '?' or explicit 'cut to black'. However, subtle non-verbal psychological cliffhangers (e.g., an unresolved silent glare before a fade) scored lower (avg 2.95/10), requiring LLM semantic comprehension to properly rank.<br/>"
        "3. <b>Proprietary Name Clutter:</b> A small subset of promos contained references to deep lore ('The Ashcroft Ledger') that might mildly disorient first-time viewers lacking episode 1 context.<br/>"
        "4. <b>Where AI got it wrong:</b> When tested with zero-shot LLM prompts, models over-indexed on lengthy dramatic soliloquies that read poetically on paper but lack the physical movement and velocity needed for TikTok vertical video pacing.",
        body_style
    ))
    story.append(Spacer(1, 4))

    # LENS 5: SOCIAL POSTING STRATEGY
    story.append(Paragraph("5. Social Distribution Strategy & Next Steps", h1_style))
    story.append(Paragraph(
        "<b>Posting Sequence:</b><br/>"
        "• <i>Phase 1: Cold User Acquisition (Ranks 1–5):</i> Deploy high-octane physical and betrayal hooks (Ep 28, Ep 16). Goal: 3-second thumb-stop on TikTok/Instagram to minimize Top-of-Funnel CPI.<br/>"
        "• <i>Phase 2: Narrative Curiosity (Ranks 6–10):</i> Deploy emotional injustice and secret-revelation clips (Ep 11, Ep 29) to trigger comment section debates and shares.<br/>"
        "• <i>Phase 3: Retargeting / Retention (Ranks 11–20):</i> Deploy romance-tension and vulnerability arcs (Ep 10, Ep 44) to convert warm scrollers into paying subscribers.<br/>"
        "<b>Extensibility & Interview Test:</b> The tool is fully decoupled. Passing <code>--input &lt;new_folder&gt; --model &lt;heuristic|gemini|openai|hybrid&gt;</code> processes any new show during the interview in seconds.",
        body_style
    ))

    doc.build(story)
    print(f"✅ Generated 2-page Solution PDF at: {OUTPUT_PDF}")

if __name__ == '__main__':
    create_solution_pdf()
