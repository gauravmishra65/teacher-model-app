QUESTION_TYPE_INSTRUCTIONS = {
    "Multiple Choice (MCQ)": """
MULTIPLE CHOICE QUESTIONS
- Write clear stem questions with 4 options (a)(b)(c)(d)
- Only one correct answer per question
- Show marks in brackets after each question
- Example:
  Q1. Which of the following is correct? [1 mark]
      (a) Option A  (b) Option B  (c) Option C  (d) Option D
""",

    "Case Study MCQ": """
CASE STUDY BASED MULTIPLE CHOICE QUESTIONS
- Write a realistic 100–150 word case study / passage / scenario relevant to the topic
- Follow it with 4–5 MCQs that can only be answered by reading the passage
- Format exactly as:

  CASE STUDY:
  ─────────────────────────────────────────────────────
  [Write the passage here. Make it factual, curriculum-aligned, and engaging.]
  ─────────────────────────────────────────────────────
  Answer the following questions based on the case study above:

  Q[n]. [Question referencing the passage] [marks]
        (a) Option A  (b) Option B  (c) Option C  (d) Option D
""",

    "Picture-Based MCQ": """
PICTURE BASED MULTIPLE CHOICE QUESTIONS
CRITICAL RULE: The SVG diagram and the questions MUST be tightly coupled.
Follow these steps IN ORDER for EACH picture-based question block:

  STEP 1 — Decide exactly what the diagram shows and list every labelled part.
           Example: "Diagram: Plant Cell. Labels — A=Cell Wall, B=Nucleus, C=Chloroplast, D=Vacuole"

  STEP 2 — Draw the SVG using ONLY those exact labels. Every label in the SVG must
           appear as a <text> element. No other labels, no unlabelled arrows.

  STEP 3 — Write MCQs that ONLY refer to labels A, B, C, D that exist in the SVG.
           Never ask about a part that is not drawn and labelled in the diagram.

Format:
  <SVG_DIAGRAM>
  <svg xmlns="http://www.w3.org/2000/svg" width="500" height="320" style="background:white;">
    <!-- shapes for each part, then <text> labels exactly matching step 1 -->
  </svg>
  </SVG_DIAGRAM>
  Study the diagram above carefully and answer the following:

  Q[n]. What is the function of the part labelled B in the diagram? [1 mark]
        (a) Option A  (b) Option B  (c) Option C  (d) Option D
""",

    "Fill in the Blanks (Picture-Based)": """
PICTURE BASED FILL IN THE BLANKS
CRITICAL RULE: The SVG diagram and the questions MUST be tightly coupled.
Follow these steps IN ORDER for EACH picture-based question block:

  STEP 1 — Decide exactly what the diagram shows and list every labelled part.
           Example: "Diagram: Water Cycle. Labels — A=Evaporation, B=Condensation, C=Precipitation, D=Runoff"

  STEP 2 — Draw the SVG using ONLY those exact labels as <text> elements.
           Every label you plan to ask about MUST be visible in the diagram.

  STEP 3 — Write fill-in-the-blank sentences that ONLY reference labels that exist in the SVG.
           The correct answer for each blank must be the exact name of the labelled part.

Format:
  <SVG_DIAGRAM>
  <svg xmlns="http://www.w3.org/2000/svg" width="500" height="320" style="background:white;">
    <!-- shapes and <text> label elements matching step 1 exactly -->
  </svg>
  </SVG_DIAGRAM>
  Look at the diagram above and fill in the blanks:

  Q[n]. The stage labelled A in the diagram is called _____________. [1 mark]
  Q[n]. The process shown at label C is known as _____________. [1 mark]
""",

    "Short Answer": """
SHORT ANSWER QUESTIONS
- Require 2–5 sentence answers
- Show marks clearly
- Example: Q[n]. Define [concept] and give one example. [2 marks]
""",

    "Long Answer": """
LONG ANSWER QUESTIONS
- Require detailed explanations, derivations, or structured responses
- Show marks clearly
- Example: Q[n]. Explain [concept] with a diagram. [5 marks]
""",

    "Fill in the Blanks": """
FILL IN THE BLANKS
- Simple fill-in-the-blank sentences, one blank per sentence
- Use underscores: _____________
- Example: Q[n]. The speed of light is _____________ m/s. [1 mark]
""",

    "True / False": """
TRUE / FALSE QUESTIONS
- Clear declarative statements — student marks True or False
- Example: Q[n]. Water boils at 90°C at sea level. (True / False) [1 mark]
""",

    "Match the Following": """
MATCH THE FOLLOWING
- Two columns: Column A (terms/questions) and Column B (answers/definitions)
- Format:
  Match Column A with Column B:
  Column A          | Column B
  1. [Term]         | (a) [Definition]
  2. [Term]         | (b) [Definition]
""",
}


def build_paper_prompt(
    subject: str,
    grade: str,
    board: str,
    topics: str,
    num_questions: int,
    difficulty: str,
    total_marks: int,
    duration: str,
    question_types: list[str],
    special_instructions: str = "",
) -> str:
    if not question_types:
        question_types = ["Multiple Choice (MCQ)", "Short Answer", "Long Answer"]

    type_instructions = "\n".join(
        QUESTION_TYPE_INSTRUCTIONS.get(t, f"\n{t.upper()}\n- Standard format\n")
        for t in question_types
    )

    has_picture_types = any(
        "picture" in t.lower() or "diagram" in t.lower()
        for t in question_types
    )

    picture_note = """
⚠ NOTE FOR PICTURE-BASED QUESTIONS:
Since this paper is AI-generated, all picture/diagram references are described in detail
inside labelled boxes. The teacher must insert or draw the actual image in those boxes
before printing. The descriptions are precise enough to recreate or source the correct image.
""" if has_picture_types else ""

    instructions_block = f"\nSpecial Instructions from Teacher: {special_instructions}" if special_instructions else ""

    marks_per_type = total_marks // len(question_types)

    return f"""You are an expert teacher and curriculum specialist. Generate a COMPLETE, print-ready question paper AND a full answer sheet.

REQUIREMENTS:
- Subject: {subject}
- Class / Grade: {grade}
- Board / Curriculum: {board}
- Topics: {topics}
- Total Questions: {num_questions} (distribute across sections)
- Question Types Required: {', '.join(question_types)}
- Difficulty: {difficulty}
- Total Marks: {total_marks} (distribute ~{marks_per_type} marks per section)
- Duration: {duration}{instructions_block}

QUESTION TYPE FORMATTING RULES — follow these exactly:
{type_instructions}
{picture_note}

═══════════════════════════════════════════════════════
OUTPUT FORMAT — use these EXACT separators:
═══════════════════════════════════════════════════════

==QUESTION PAPER==

[SCHOOL NAME / INSTITUTION]
Subject: {subject.upper()} — MODEL QUESTION PAPER
Class: {grade}  |  Board: {board}  |  Maximum Marks: {total_marks}  |  Time Allowed: {duration}

General Instructions:
1. All questions are compulsory unless stated otherwise.
2. Read each question carefully before answering.
3. Marks for each question are indicated in [ ].
4. For picture-based questions, refer to the diagram/picture provided.

[Write each section below with its heading, instructions, and all questions.
One section per question type. Cover all topics proportionally.]

==ANSWER SHEET==

ANSWER KEY & MARKING SCHEME
Subject: {subject}  |  Class: {grade}  |  Total Marks: {total_marks}

Instructions for Evaluators:
- Award marks strictly as per marking scheme.
- For fill-in-the-blank and short answer, accept any correct equivalent answer.

[Provide complete answers for EVERY question in the same order as the paper.
Format each answer as:

Q[number]. [Full correct answer]
[Marks]: [X] marks
[Key Points]: • point 1 • point 2 (for short/long answers)

For MCQs: state correct option letter + answer text + one-line explanation.
For Fill in the Blank: state the exact word/phrase.
For Case Study MCQs: state correct option with reference to the passage.
For Picture-Based: state the answer with reference to the labelled part.]
"""
