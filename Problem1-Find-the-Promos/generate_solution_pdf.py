"""
GENERATE 2-PAGE SOLUTION PDF FOR PROBLEM 1
==========================================
Delegates to the master generator to create the clean, easy-to-read 2-page Times New Roman PDF.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from generate_all_solution_pdfs import generate_problem_1_pdf

OUTPUT_PDF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Solution_Doc_Kuku_AI_Generalist.pdf")

if __name__ == "__main__":
    generate_problem_1_pdf(OUTPUT_PDF)
    print(f"Generated clean Solution PDF: {OUTPUT_PDF}")
