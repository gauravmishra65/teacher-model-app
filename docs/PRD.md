# Product Requirements Document
## Teacher Model Question Paper Generator

---

### 1. Problem Statement
Teachers spend significant time designing quality question papers. They need a tool that leverages multiple AI models to collaboratively draft, critique, and synthesise a final model question paper — saving time while improving quality.

---

### 2. Core User Persona
**Primary User:** School/college teacher (any subject, grades 1–12 and undergraduate)
- Needs: Fast, curriculum-aligned, well-structured question papers
- Pain point: Creating balanced papers covering all topics with correct difficulty spread

---

### 3. Key User Stories
- As a teacher, I want to enter subject/class/topic details so the app understands my requirement
- As a teacher, I want 3 AI models to each draft a question paper so I get diverse perspectives
- As a teacher, I want the models to critique each other's drafts so weak questions are challenged
- As a teacher, I want a synthesised final paper so I get the best of all three
- As a teacher, I want to download the final paper as a Word doc so I can print or edit it

---

### 4. Functional Requirements

#### 4.1 Input Form
| Field | Type | Required |
|---|---|---|
| Subject | Text | Yes |
| Class / Grade | Dropdown (1–12 + UG) | Yes |
| Board / Curriculum | Text (CBSE, ICSE, State, etc.) | Yes |
| Topics to cover | Text area | Yes |
| Number of questions | Number | Yes |
| Difficulty level | Slider (Easy / Medium / Hard mix) | Yes |
| Total marks | Number | Yes |
| Exam duration | Dropdown | Yes |
| Special instructions | Text area | No |

#### 4.2 Multi-Model Debate Flow
1. **Round 1 — Parallel Draft:** Claude, Gemini, Llama each independently generate a question paper
2. **Round 2 — Peer Critique:** Each model reviews the other two drafts and suggests improvements
3. **Round 3 — Synthesis:** Claude reads all 3 drafts + all 3 critiques and produces the final paper

#### 4.3 Output
- Streamed progress visible in UI during each round
- Final question paper displayed in the app
- Download as formatted `.docx` file

---

### 5. Non-Functional Requirements
- All 3 Round 1 calls run in parallel (async) to minimise wait time
- API keys stored in `.env` file, never hardcoded
- Graceful fallback if one model's API fails (continue with remaining models)

---

### 6. Tech Stack
| Layer | Choice |
|---|---|
| Frontend | Streamlit |
| Backend | Python (async) |
| Claude | `anthropic` SDK |
| Gemini | `google-generativeai` SDK |
| Llama | `groq` SDK (Llama 3 on Groq) |
| Word output | `python-docx` |
| Env management | `python-dotenv` |

---

### 7. North Star Metric
**Teacher acceptance rate** — percentage of generated papers a teacher uses with ≤ 20% manual edits.

---

### 8. Key Assumptions to Validate
1. 3 models produce meaningfully different papers (not near-identical outputs)
2. Peer critique round improves final paper quality vs. single-model output
3. Teachers prefer Word format over PDF for editability
4. Groq's Llama is fast enough to not bottleneck the parallel round

---

### 9. Out of Scope (v1)
- User accounts / saved paper history
- Image/diagram questions
- Auto-marking scheme generation
- LMS integration
