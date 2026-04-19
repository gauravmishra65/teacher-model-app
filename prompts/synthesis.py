def build_synthesis_prompt(
    drafts: dict[str, str],
    critiques: dict[str, str],
    subject: str,
    grade: str,
    board: str,
    total_marks: int,
    num_questions: int,
    duration: str,
) -> str:
    drafts_block = "\n\n".join(
        f"=== DRAFT by {name} ===\n{draft}" for name, draft in drafts.items()
    )
    critiques_block = "\n\n".join(
        f"=== CRITIQUE by {name} ===\n{critique}" for name, critique in critiques.items()
    )
    return f"""You are the final synthesiser producing the definitive question paper for a teacher.

You have received question paper drafts from three AI models and their peer critiques. Your job is to produce the BEST possible final paper.

SUBJECT: {subject} | GRADE: {grade} | BOARD: {board}
TOTAL MARKS: {total_marks} | QUESTIONS: {num_questions} | DURATION: {duration}

--- ALL DRAFTS ---
{drafts_block}

--- ALL CRITIQUES ---
{critiques_block}

SYNTHESIS RULES:
1. Select the strongest, clearest questions from across all three drafts
2. Address every valid criticism raised — fix ambiguous questions, fill topic gaps
3. Ensure the final paper has perfect mark distribution adding up to exactly {total_marks}
4. Maintain clear section structure with instructions
5. Do NOT copy-paste weaknesses — rewrite or replace any poor questions
6. The final paper must be print-ready and complete

Output ONLY the final formatted question paper — no meta-commentary, no preamble."""
