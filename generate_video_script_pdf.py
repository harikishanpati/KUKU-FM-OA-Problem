"""
GENERATE VIDEO WALKTHROUGH SCRIPTS & RECORDING GUIDE PDF
========================================================
Creates a clean, highly readable, printable PDF guide with word-for-word scripts
for Kuku AI Generalist video walkthrough submissions.
"""

import os
import sys
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PDF = os.path.join(BASE_DIR, "Video_Walkthrough_Scripts_Guide.pdf")

CANDIDATE_NAME = "Harikishan Pati"
ROLL_NO = "722MM1051"
BRANCH = "Metallurgical and Materials Engineering"
GITHUB_LINK = "https://github.com/harikishanpati/KUKU-FM-OA-Problem"

P1_STREAMLIT = "https://kuku-fm-oa-problem1.streamlit.app/"
P2_STREAMLIT = "https://kuku-fm-oa-problem2.streamlit.app/"
P3_STREAMLIT = "https://kuku-fm-oa-problem-3.streamlit.app/"


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Times-Roman", 9)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Bottom rule & footer
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(36, 30, 612 - 36, 30)
        
        self.drawString(36, 18, f"Kuku AI Generalist | Video Walkthrough Guide | Harikishan Pati ({ROLL_NO})")
        self.drawRightString(612 - 36, 18, f"Page {self._pageNumber} of {page_count}")
        
        # Top subtle running header on page > 1
        if self._pageNumber > 1:
            self.drawString(36, 792 - 24, "KUKU AI GENERALIST — VIDEO RECORDING GUIDE & SCRIPTS")
            self.drawRightString(612 - 36, 792 - 24, "WALKTHROUGH SCRIPTS")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(36, 792 - 27, 612 - 36, 792 - 27)

        self.restoreState()


def get_styles():
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'],
        fontName='Times-Bold', fontSize=15, leading=18,
        textColor=colors.HexColor('#B81D13')
    )

    h1 = ParagraphStyle(
        'SectionH1', parent=styles['Normal'],
        fontName='Times-Bold', fontSize=12.5, leading=16,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=8, spaceAfter=4
    )

    h2 = ParagraphStyle(
        'SectionH2', parent=styles['Normal'],
        fontName='Times-Bold', fontSize=11, leading=14,
        textColor=colors.HexColor('#B81D13'),
        spaceBefore=6, spaceAfter=3
    )

    body = ParagraphStyle(
        'BodyComfortable', parent=styles['Normal'],
        fontName='Times-Roman', fontSize=10.5, leading=14.5,
        textColor=colors.HexColor('#1E293B')
    )

    bullet_style = ParagraphStyle(
        'BulletComfortable', parent=body,
        leftIndent=14, firstLineIndent=-8,
        spaceAfter=3
    )

    meta_left = ParagraphStyle(
        'MetaLeft', parent=styles['Normal'],
        fontName='Times-Bold', fontSize=11, leading=14,
        textColor=colors.HexColor('#0F172A')
    )

    meta_right = ParagraphStyle(
        'MetaRight', parent=styles['Normal'],
        fontName='Times-Roman', fontSize=9, leading=12,
        textColor=colors.HexColor('#334155')
    )

    table_header = ParagraphStyle(
        'TableHeader', parent=styles['Normal'],
        fontName='Times-Bold', fontSize=9.5, leading=12,
        textColor=colors.white
    )

    time_col = ParagraphStyle(
        'TimeCol', parent=styles['Normal'],
        fontName='Times-Bold', fontSize=9, leading=12,
        textColor=colors.HexColor('#B81D13')
    )

    action_col = ParagraphStyle(
        'ActionCol', parent=styles['Normal'],
        fontName='Times-Italic', fontSize=9, leading=12,
        textColor=colors.HexColor('#1D4ED8')
    )

    speech_col = ParagraphStyle(
        'SpeechCol', parent=styles['Normal'],
        fontName='Times-Roman', fontSize=9.5, leading=13,
        textColor=colors.HexColor('#0F172A')
    )

    tip_box = ParagraphStyle(
        'TipBox', parent=styles['Normal'],
        fontName='Times-Roman', fontSize=9.5, leading=13.5,
        textColor=colors.HexColor('#1E293B')
    )

    return {
        'title': title_style,
        'h1': h1,
        'h2': h2,
        'body': body,
        'bullet': bullet_style,
        'meta_left': meta_left,
        'meta_right': meta_right,
        'table_header': table_header,
        'time_col': time_col,
        'action_col': action_col,
        'speech_col': speech_col,
        'tip_box': tip_box
    }


def make_header_banner(title, subtitle, styles):
    content = [
        [
            Paragraph(
                f"<font color='#B81D13'><b>KUKU AI GENERALIST ASSIGNMENT</b></font><br/>"
                f"<b>{title}</b><br/>"
                f"<font color='#64748B' size='8.5'>{subtitle}</font>",
                styles['meta_left']
            ),
            Paragraph(
                f"<b>Candidate:</b> {CANDIDATE_NAME} (Roll: {ROLL_NO})<br/>"
                f"<b>Branch:</b> {BRANCH}<br/>"
                f"<b>GitHub:</b> <font color='#2563EB'><u>{GITHUB_LINK}</u></font><br/>"
                f"<b>Evaluation Limit:</b> Up to 3 minutes screen recording",
                styles['meta_right']
            )
        ]
    ]

    t = Table(content, colWidths=[310, 230])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    return t


def make_callout(title, text, styles, accent_color='#B81D13', bg_color='#F8FAFC'):
    cell_data = [[
        Paragraph(f"<b><font color='{accent_color}'>{title}</font></b><br/>{text}", styles['tip_box'])
    ]]
    t = Table(cell_data, colWidths=[540])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(bg_color)),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('LINELEFT', (0,0), (0,-1), 3.5, colors.HexColor(accent_color)),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
    ]))
    return t


def build_script_table(data_rows, styles):
    table_data = [
        [
            Paragraph("Timestamp", styles['table_header']),
            Paragraph("What to Do on Screen (Visual Action)", styles['table_header']),
            Paragraph("What to Say (Word-for-Word Script)", styles['table_header'])
        ]
    ]
    for row in data_rows:
        table_data.append([
            Paragraph(row[0], styles['time_col']),
            Paragraph(row[1], styles['action_col']),
            Paragraph(row[2], styles['speech_col'])
        ])

    t = Table(table_data, colWidths=[65, 175, 300])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    return t


def generate_guide_pdf():
    styles = get_styles()
    doc = SimpleDocTemplate(
        OUTPUT_PDF, pagesize=letter,
        leftMargin=36, rightMargin=36, topMargin=28, bottomMargin=32
    )
    story = []

    # =========================================================================
    # PAGE 1: SETUP GUIDE & CHECKLIST
    # =========================================================================
    story.append(make_header_banner(
        "Walkthrough Video Production Guide & Scripts",
        "Screen recording setup, timing rules, and word-for-word scripts for all 3 problems",
        styles
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("1. Kuku Video Submission Requirement (From Guidelines)", styles['h1']))
    kuku_guideline = (
        "<b>Requirement:</b> Up to 3 minutes screen recording in your own voice showing your solution running.<br/>"
        "<b>Purpose:</b> Quickest way for evaluators to see your work the way you meant it.<br/>"
        "<b>Permitted Formats:</b> Loom link, unlisted YouTube video, or Google Drive link (accessible to anyone with link)."
    )
    story.append(make_callout("OFFICIAL KUKU WALKTHROUGH CRITERIA", kuku_guideline, styles, accent_color='#B81D13'))
    story.append(Spacer(1, 6))

    story.append(Paragraph("2. Pre-Recording Setup Checklist (Takes 2 Minutes)", styles['h1']))
    story.append(Paragraph("- <b>Recommended Tool:</b> <b>Loom (Free)</b> is the easiest. It records your screen + circular webcam bubble in the corner and creates an instant shareable link. Alternatively, use <b>OBS Studio</b> or press <code>Win + Alt + R</code> (Windows Game Bar).", styles['bullet']))
    story.append(Paragraph("- <b>Browser Zoom:</b> In Google Chrome, press <code>Ctrl + +</code> to zoom your Streamlit tab to <b>110% or 125%</b> so all metrics, charts, and buttons are crystal clear on mobile/laptop screens.", styles['bullet']))
    story.append(Paragraph("- <b>Tab Preparation:</b> Open 3 browser tabs beforehand: (1) Your Live Streamlit App, (2) Your GitHub Repository, and (3) Your 2-page Solution PDF.", styles['bullet']))
    story.append(Paragraph("- <b>Audio & Voice:</b> Use basic earphones or a laptop microphone. Speak naturally at a steady pace. Do not rush; the script is timed for a comfortable 2.5 minutes.", styles['bullet']))
    story.append(Paragraph("- <b>Timing Sweet Spot:</b> Keep each video between <b>2 minutes 15 seconds and 2 minutes 45 seconds</b> (strictly under the 3-minute hard ceiling).", styles['bullet']))
    story.append(Spacer(1, 6))

    story.append(Paragraph("3. The 5-Step Structure Every Winning Demo Follows", styles['h1']))
    story.append(Paragraph("1. <b>Hook & Problem (0:00 - 0:25):</b> Introduce yourself, state the problem, and why it matters to Kuku.", styles['bullet']))
    story.append(Paragraph("2. <b>Live Interactive Demo (0:25 - 1:15):</b> Show the tool running live. Click buttons, show metrics, and explain outputs.", styles['bullet']))
    story.append(Paragraph("3. <b>Customization & Edge Cases (1:15 - 1:45):</b> Demonstrate sliders, weight adjustments, or safety escalations.", styles['bullet']))
    story.append(Paragraph("4. <b>Validation & Honest Limits (1:45 - 2:15):</b> Mention real results on Kuku's 50 episodes and honest failure boundaries.", styles['bullet']))
    story.append(Paragraph("5. <b>Scale & Sign-off (2:15 - 2:30):</b> Mention sub-second speed, zero compute cost, and GitHub links.", styles['bullet']))
    story.append(Spacer(1, 8))

    story.append(make_callout(
        "LIVE STREAMLIT LINKS FOR RECORDING",
        f"• <b>Problem 1 (Promos):</b> <font color='#2563EB'><u>{P1_STREAMLIT}</u></font><br/>"
        f"• <b>Problem 2 (NyayaAI):</b> <font color='#2563EB'><u>{P2_STREAMLIT}</u></font><br/>"
        f"• <b>Problem 3 (Localization):</b> <font color='#2563EB'><u>{P3_STREAMLIT}</u></font><br/>"
        f"• <b>GitHub Repository:</b> <font color='#2563EB'><u>{GITHUB_LINK}</u></font>",
        styles, accent_color='#2563EB', bg_color='#EFF6FF'
    ))

    # =========================================================================
    # PAGE 2: PROBLEM 1 SCRIPT
    # =========================================================================
    story.append(PageBreak())

    story.append(Paragraph("Script 1: Problem 1 — Automated Promo Finder & Ranking Studio", styles['h1']))
    story.append(Paragraph(
        f"<b>App URL:</b> <font color='#2563EB'><u>{P1_STREAMLIT}</u></font> | <b>Target Time:</b> ~2:30 minutes | <b>Style:</b> Confident & Professional",
        styles['body']
    ))
    story.append(Spacer(1, 4))

    p1_rows = [
        (
            "0:00 - 0:25\n(25 sec)",
            "Start on the Streamlit dashboard home screen. Cursor hovering near the title banner.",
            "\"Hi everyone, I'm Harikishan Pati. In vertical microdramas on TikTok, Instagram Reels, and YouTube Shorts, user attention is won or lost in the first three seconds. Today, human video editors spend 4 to 6 hours per 50-episode show reading through scripts to find good promo cuts. My solution completely automates this: it scans all 50 screenplay episodes, evaluates 20-to-60 second candidate scenes, and outputs the top 20 viral promos in just 1.5 seconds at zero compute cost.\""
        ),
        (
            "0:25 - 1:10\n(45 sec)",
            "Scroll down Tab 1 (Top Ranked Promos). Click on the top promo card to reveal the dialogue and tags.",
            "\"Here is our live dashboard. Every candidate clip is scored across five core factors: a 30% Hook weight, 25% Emotional intensity, 20% Conflict, 15% Cliffhanger ending, and 10% Standalone clarity. Looking at our top-ranked promo from Episode 1: it immediately hooks the viewer with high emotional stakes, maintains natural speech boundaries without cutting characters off mid-sentence, and cleanly terminates on a dramatic cliffhanger question.\""
        ),
        (
            "1:10 - 1:40\n(30 sec)",
            "Move cursor to the left sidebar. Adjust the Hook slider and point to the Model Architecture selector.",
            "\"In the sidebar, marketing directors can customize weights dynamically. If a campaign needs pure cliffhangers, they can dial up the cliffhanger weight. Crucially, the architecture features a swappable model layer: our offline rule-based heuristic runs instantly for free, and can be seamlessly upgraded to Gemini Flash or GPT-4o-mini for semantic scoring.\""
        ),
        (
            "1:40 - 2:05\n(25 sec)",
            "Click on Tab 2 (Quality & Failure Analysis). Point to the 100% pass rate and catalog variety.",
            "\"For quality control, we audited this across all 50 episodes of 'I Married a Broken Soldier'. 100% of our clips adhere to the 20-to-60 second platform limit. To prevent Episode 1 from monopolizing all promos, our diversity filter caps each episode at 2 cuts, giving marketing 17 distinct episodes. In terms of failure modes: text scripts cannot capture non-verbal acting chemistry or quiet visual cliffhangers, which is where hybrid LLM scoring adds value.\""
        ),
        (
            "2:05 - 2:30\n(25 sec)",
            "Switch to GitHub repository tab briefly, then back to the dashboard.",
            "\"The entire system is production-ready, runs via CLI as well as this web app, and processes a 100-episode season in under 4 seconds. The code, test suite, and 2-page solution PDF are linked on GitHub. Thank you!\""
        )
    ]
    story.append(build_script_table(p1_rows, styles))

    # =========================================================================
    # PAGE 3: PROBLEM 2 SCRIPT
    # =========================================================================
    story.append(PageBreak())

    story.append(Paragraph("Script 2: Problem 2 — NyayaAI: Everyday Indian Legal Co-Pilot", styles['h1']))
    story.append(Paragraph(
        f"<b>App URL:</b> <font color='#2563EB'><u>{P2_STREAMLIT}</u></font> | <b>Target Time:</b> ~2:30 minutes | <b>Style:</b> Empathetic & Law-Grounded",
        styles['body']
    ))
    story.append(Spacer(1, 4))

    p2_rows = [
        (
            "0:00 - 0:25\n(25 sec)",
            "Start on the NyayaAI dashboard. Hover over the title and ethics ground rules.",
            "\"Hi everyone, I'm Harikishan Pati. Millions of everyday Indians face unfair disputes: landlords refusing to return security deposits of Rs. 30,000 to Rs. 80,000, shopping portals denying refunds for damaged goods, or employers withholding final salaries. Hiring an advocate costs Rs. 15,000 to Rs. 50,000, which is unviable for claims under Rs. 1 Lakh. I built NyayaAI: a free, grounded legal co-pilot that turns everyday stories into actionable legal notices.\""
        ),
        (
            "0:25 - 1:15\n(50 sec)",
            "In the sidebar dropdown, select 'Case 1: Bangalore Landlord Keeping Deposit'. Click 'Analyze My Case'.",
            "\"Watch how it works. A tenant explains in conversational Hinglish that their Bangalore landlord withheld a Rs. 65,000 deposit for repainting. When we analyze the case, NyayaAI extracts the financial stake, identifies existing proof like WhatsApp chats, and flags missing evidence like inspection photos. Most importantly, it applies real codified Indian law: Section 108 of the Transfer of Property Act, which explicitly bars deductions for normal wear and tear.\""
        ),
        (
            "1:15 - 1:45\n(30 sec)",
            "Scroll down the right column to show the auto-generated 15-Day Legal Demand Notice.",
            "\"Below the analysis, it automatically drafts a formal 15-day Legal Demand Notice. This cites the statutory sections, specifies the Rs. 65,000 claim, and warns of escalation to the Bangalore Rent Authority and Civil Court. Over 65% of civil disputes are resolved right at this stage without hiring a lawyer.\""
        ),
        (
            "1:45 - 2:10\n(25 sec)",
            "Select 'Case 4: Recovery Agent Police Arrest Threat' from the sidebar dropdown. Click 'Analyze'.",
            "\"Ethical guardrails are the most critical feature. Generative AI must never hallucinate fake laws or handle criminal intimidation casually. If a user enters a recovery agent making fake police arrest threats, watch what happens: [Point to RED BANNER] NyayaAI immediately halts civil drafting, triggers a critical alert under IPC Section 384 for extortion, and routes the citizen to the National Cybercrime Helpline 1930.\""
        ),
        (
            "2:10 - 2:30\n(20 sec)",
            "Scroll back up and conclude with scalability and zero cost.",
            "\"The engine executes in 0.2 seconds at zero API cost, ensuring complete privacy and zero hallucinations. It easily scales to 100,000+ daily citizens on standard cloud infrastructure. Thank you!\""
        )
    ]
    story.append(build_script_table(p2_rows, styles))

    # =========================================================================
    # PAGE 4: PROBLEM 3 SCRIPT
    # =========================================================================
    story.append(PageBreak())

    story.append(Paragraph("Script 3: Problem 3 — Microdrama Pacing & Localization Auditor", styles['h1']))
    story.append(Paragraph(
        f"<b>App URL:</b> <font color='#2563EB'><u>{P3_STREAMLIT}</u></font> | <b>Target Time:</b> ~2:30 minutes | <b>Style:</b> Technical & Direct",
        styles['body']
    ))
    story.append(Spacer(1, 4))

    p3_rows = [
        (
            "0:00 - 0:25\n(25 sec)",
            "Start on the auditor dashboard, highlighting the top 4 metric cards.",
            "\"Hi everyone, I'm Harikishan Pati. In mobile microdramas, audience retention is driven by audio pacing. Screenwriters write for the page, not the stopwatch. This leads to two critical defects: dialogue rushed above 185 words per minute, which clips voice actors and AI dubbing; and dead air silences over 3.2 seconds, which cause 40% of mobile viewers to swipe away. Fixing this post-recording costs 10 times more. I built this pre-recording Pacing & Localization Auditor.\""
        ),
        (
            "0:25 - 1:05\n(40 sec)",
            "Point cursor to the 4 KPI metric cards across the top of the dashboard.",
            "\"Across all 50 full episodes of 'I Married a Broken Soldier'—totaling 1,487 dialogue lines—the auditor completed a full pass in 0.8 seconds. It uncovered an average catalog health score of just 54.8%, identifying 397 rushed lines that would distort audio synthesis and 147 dead air retention gaps.\""
        ),
        (
            "1:05 - 1:45\n(40 sec)",
            "Select Episode 1 from the episode dropdown. Expand the first dialogue issue on the left.",
            "\"Let's look at Episode 1. In line 1, Lady Juliana speaks at 245 WPM—9 words crammed into just 2.2 seconds. Rather than just flagging an error, our tool gives actionable mathematical fixes: either add 1.5 seconds of timeline breathing room, or trim exactly 4 words to achieve a natural 150 WPM cadence.\""
        ),
        (
            "1:45 - 2:10\n(25 sec)",
            "Move cursor to the right column (Dead Air Retention Hazards). Expand the 8.3s silence issue.",
            "\"On the right column, the auditor flags retention hazards. In Episode 1, there is an 8.3-second gap of total silence before dialogue begins. In a vertical video feed, viewers assume the app froze. The tool flags this so the audio editor can insert ambient music or tighten the edit before voice actors enter the recording booth.\""
        ),
        (
            "2:10 - 2:30\n(20 sec)",
            "Scroll down to the production impact section at the bottom.",
            "\"By serving as an automated pre-recording CI/CD gate, this tool saves hundreds of studio re-recording hours and protects algorithmic watch-time on TikTok and Kuku TV. All 50 episode audit logs and the solution doc are available on GitHub. Thank you!\""
        )
    ]
    story.append(build_script_table(p3_rows, styles))

    # =========================================================================
    # PAGE 5: COMBINED 3-MINUTE MASTER SCRIPT & SUBMISSION GUIDE
    # =========================================================================
    story.append(PageBreak())

    story.append(Paragraph("Bonus Script: All-In-One 3-Minute Master Walkthrough", styles['h1']))
    story.append(Paragraph(
        "Use this single 3-minute script if you prefer to record <b>one single video covering all 3 problems back-to-back</b> (60 seconds per problem).",
        styles['body']
    ))
    story.append(Spacer(1, 4))

    all_in_one_rows = [
        (
            "0:00 - 0:15\n(15 sec)",
            "Show GitHub repository or title slide.",
            "\"Hi, I'm Harikishan Pati, presenting my end-to-end solutions for the Kuku AI Generalist Assignment across all three problems.\""
        ),
        (
            "0:15 - 1:00\n(45 sec)",
            "Switch to Problem 1 Streamlit App. Scroll to Top Promos and adjust slider in sidebar.",
            "\"Problem 1 is our Microdrama Promo Studio. It scans 50 screenplay episodes, evaluates 30-to-50 second scenes using our 5-factor retention formula, and extracts the top 20 viral clips in 1.5 seconds at zero cost. Marketing teams can adjust hook, emotion, and cliffhanger weights live in the sidebar.\""
        ),
        (
            "1:00 - 1:55\n(55 sec)",
            "Switch to Problem 2 Streamlit App. Run Case 1 (deposit) and show Case 4 (threat warning).",
            "\"Problem 2 is NyayaAI, an everyday legal co-pilot for rent, refund, and wage disputes. It takes natural Hinglish stories, maps them to verified Indian statutes like Section 108 of the Transfer of Property Act, and auto-drafts a 15-day Legal Demand Notice. If criminal threats are detected, it enforces strict ethical guardrails, immediately halting drafting and routing the user to the 1930 Cyber Helpline.\""
        ),
        (
            "1:55 - 2:45\n(50 sec)",
            "Switch to Problem 3 Streamlit App. Show the 4 metrics and the Episode 1 WPM and Dead Air fixes.",
            "\"Problem 3 is our Pacing & Localization Auditor. It audits 50 episodes in 0.8 seconds to eliminate rushed speech over 185 WPM and dead air silences over 3.2 seconds before audio recording. It tells editors exactly how many words to cut or seconds to add to preserve TikTok retention.\""
        ),
        (
            "2:45 - 3:00\n(15 sec)",
            "Switch to GitHub Repository showing the clean directory structure and PDF solution files.",
            "\"All 3 interactive apps are live on Streamlit Cloud, backed by complete test suites and 2-page solution documents in the repository. Thank you!\""
        )
    ]
    story.append(build_script_table(all_in_one_rows, styles))
    story.append(Spacer(1, 8))

    story.append(Paragraph("How to Submit Your Video Links", styles['h1']))
    story.append(Paragraph("1. <b>Loom:</b> Simply copy the public share link from Loom (e.g. <code>https://www.loom.com/share/...</code>).", styles['bullet']))
    story.append(Paragraph("2. <b>YouTube:</b> Set video visibility to <b>'Unlisted'</b>. This allows anyone with the link to watch it without it appearing in public search results.", styles['bullet']))
    story.append(Paragraph("3. <b>Google Drive:</b> Click Share -> change General Access to <b>'Anyone with the link can view'</b>.", styles['bullet']))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"✅ Generated Video Guide PDF: {OUTPUT_PDF}")


if __name__ == "__main__":
    generate_guide_pdf()
