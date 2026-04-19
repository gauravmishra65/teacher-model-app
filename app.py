import os
import re
import sys
import streamlit as st
from dotenv import load_dotenv

load_dotenv(encoding="utf-8", override=True)

# On Streamlit Cloud, secrets are in st.secrets — copy them into os.environ
# so the rest of the app (which uses os.environ) works unchanged.
for _k in ("GROQ_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY"):
    if _k not in os.environ:
        try:
            os.environ[_k] = st.secrets[_k]
        except Exception:
            pass

sys.path.insert(0, os.path.dirname(__file__))

from models.auto_select import get_best_model, list_available
from prompts.question_paper import build_paper_prompt
from output.docx_generator import generate_docx

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Teacher Model App",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',system-ui,sans-serif;background:#0a0f1e!important;color:#f1f5f9}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding-top:0!important;padding-bottom:2rem;max-width:100%!important}
section[data-testid="stSidebar"]{background:#0f172a!important;border-right:1px solid #1e293b!important;width:320px!important}
section[data-testid="stSidebar"]>div{padding-top:0!important}
input,textarea,select{background:#1e293b!important;border:1px solid #334155!important;color:#f1f5f9!important;border-radius:8px!important}
label{color:#94a3b8!important;font-size:12px!important;font-weight:500!important}
.stTextInput>div>div,.stTextArea>div>div,.stNumberInput>div>div{background:#1e293b!important;border:1px solid #334155!important;border-radius:8px!important}
.stSelectbox>div>div,.stMultiSelect>div>div{background:#1e293b!important;border:1px solid #334155!important;border-radius:8px!important;color:#f1f5f9!important}
.stSlider>div>div>div{background:#3b82f6!important}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#3b82f6,#2563eb)!important;color:white!important;border:none!important;border-radius:10px!important;font-weight:600!important;font-size:14px!important;padding:.65rem 1.2rem!important;box-shadow:0 4px 20px rgba(59,130,246,.35)!important;width:100%!important}
.stButton>button[kind="primary"]:hover{background:linear-gradient(135deg,#60a5fa,#3b82f6)!important}
.stDownloadButton>button{background:#0f4c75!important;color:#bfdbfe!important;border:1px solid #1e6aa7!important;border-radius:8px!important;font-weight:600!important;font-size:13px!important}
.stDownloadButton>button:hover{background:#1d6fa8!important}
.stTabs [data-baseweb="tab-list"]{background:#0f172a!important;border-bottom:1px solid #1e293b!important;gap:0!important}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:#64748b!important;font-size:13px!important;font-weight:500!important;border-bottom:2px solid transparent!important;padding:10px 20px!important}
.stTabs [aria-selected="true"]{color:#60a5fa!important;border-bottom:2px solid #3b82f6!important;background:transparent!important}
.stTabs [data-baseweb="tab-panel"]{background:#0f172a!important;border:1px solid #1e293b!important;border-top:none!important;border-radius:0 0 12px 12px!important;padding:20px!important}
.stSuccess{background:rgba(16,185,129,.1)!important;border:1px solid rgba(16,185,129,.3)!important;color:#6ee7b7!important;border-radius:8px!important}
.stWarning{background:rgba(245,158,11,.1)!important;border:1px solid rgba(245,158,11,.3)!important;color:#fcd34d!important;border-radius:8px!important}
.stError{background:rgba(239,68,68,.1)!important;border:1px solid rgba(239,68,68,.3)!important;color:#fca5a5!important;border-radius:8px!important}
hr{border-color:#1e293b!important}
::-webkit-scrollbar{width:4px}::-webkit-scrollbar-track{background:#1e293b}::-webkit-scrollbar-thumb{background:#334155;border-radius:2px}
</style>
""", unsafe_allow_html=True)

# ── Auto model selection ──────────────────────────────────────────────────────
try:
    model_label, model_caller = get_best_model()
except RuntimeError as e:
    st.error(str(e))
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # App header
    st.markdown("""
    <div style="padding:16px 4px 8px;">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
        <div style="width:34px;height:34px;border-radius:9px;background:#3b82f6;
          display:flex;align-items:center;justify-content:center;font-size:18px;">📝</div>
        <div>
          <div style="font-size:14px;font-weight:600;color:#f1f5f9;">Teacher Model App</div>
          <div style="font-size:10px;color:#64748b;">AI Question Paper Generator</div>
        </div>
      </div>
    </div>
    <hr style="border-color:#1e293b;margin:4px 0 12px;"/>
    """, unsafe_allow_html=True)

    # Active model banner
    st.markdown(f"""
    <div style="background:#0d2137;border:1px solid #1e4976;border-radius:10px;
        padding:10px 12px;margin-bottom:14px;display:flex;align-items:center;gap:10px;">
      <span style="font-size:18px;">🤖</span>
      <div>
        <div style="font-size:10px;color:#60a5fa;font-weight:600;letter-spacing:.6px;text-transform:uppercase;">Active Model</div>
        <div style="font-size:12px;color:#e2e8f0;font-weight:500;">{model_label}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size:11px;font-weight:600;color:#64748b;letter-spacing:.8px;text-transform:uppercase;margin-bottom:10px;">Paper Details</div>', unsafe_allow_html=True)

    subject = st.text_input("Subject *", placeholder="e.g. Science, Mathematics, History")
    grade   = st.selectbox("Class / Grade *", [
        "Grade 1","Grade 2","Grade 3","Grade 4","Grade 5","Grade 6",
        "Grade 7","Grade 8","Grade 9","Grade 10","Grade 11","Grade 12","Undergraduate"
    ], index=9)
    board   = st.text_input("Board / Curriculum *", placeholder="e.g. CBSE, ICSE, State Board")
    topics  = st.text_area("Topics to Cover *",
        placeholder="e.g. Photosynthesis, Cell Structure, Ecosystems", height=80)

    c1, c2 = st.columns(2)
    with c1:
        num_questions = st.number_input("Questions *", min_value=3, max_value=100, value=20)
    with c2:
        total_marks = st.number_input("Total Marks *", min_value=10, max_value=500, value=80)

    duration   = st.selectbox("Duration *",
        ["30 minutes","1 hour","1.5 hours","2 hours","2.5 hours","3 hours"], index=3)
    difficulty = st.select_slider("Difficulty",
        options=["Easy","Easy-Medium","Balanced","Medium-Hard","Hard"], value="Balanced")

    # Question types — new types prominent
    st.markdown("""
    <div style="margin:10px 0 6px;">
      <div style="font-size:11px;font-weight:600;color:#64748b;letter-spacing:.8px;text-transform:uppercase;">Question Types</div>
      <div style="font-size:10px;color:#334155;margin-top:2px;">★ = new types with picture/case support</div>
    </div>
    """, unsafe_allow_html=True)

    ALL_TYPES = [
        "Multiple Choice (MCQ)",
        "★ Case Study MCQ",
        "★ Picture-Based MCQ",
        "★ Fill in the Blanks (Picture-Based)",
        "Short Answer",
        "Long Answer",
        "Fill in the Blanks",
        "True / False",
        "Match the Following",
    ]

    selected_types = st.multiselect(
        "Select types",
        ALL_TYPES,
        default=["Multiple Choice (MCQ)", "★ Case Study MCQ", "★ Picture-Based MCQ"],
        label_visibility="collapsed",
    )

    special = st.text_area("Special Instructions",
        placeholder="e.g. Focus on diagrams, avoid calculus, include real-life examples", height=65)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    generate_btn = st.button("✨  Generate Paper + Answer Sheet", type="primary", use_container_width=True)

    # Model status panel at bottom
    st.markdown("<hr style='border-color:#1e293b;margin:14px 0 10px;'/>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:10px;font-weight:600;color:#475569;letter-spacing:.6px;text-transform:uppercase;margin-bottom:8px;">Model Status</div>', unsafe_allow_html=True)
    for m in list_available():
        dot_color = "#10b981" if m["available"] else "#374151"
        text_color = "#94a3b8" if m["available"] else "#334155"
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:7px;margin-bottom:5px;">
          <div style="width:6px;height:6px;border-radius:50%;background:{dot_color};flex-shrink:0;"></div>
          <div>
            <span style="font-size:11px;color:{text_color};font-weight:500;">{m['model']}</span>
            <span style="font-size:10px;color:#334155;margin-left:4px;">{m['note']}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)


# ── Navbar ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:#0f172a;border-bottom:1px solid #1e293b;padding:0 24px;height:48px;
    display:flex;align-items:center;justify-content:space-between;">
  <div style="font-size:13px;font-weight:600;color:#f1f5f9;">
    📝 Teacher Model App
  </div>
  <div style="display:flex;align-items:center;gap:6px;font-size:11px;color:#475569;">
    <span style="width:6px;height:6px;border-radius:50%;background:#10b981;display:inline-block;"></span>
    {model_label}
  </div>
</div>
""", unsafe_allow_html=True)
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)


# ── Render paper as styled HTML ───────────────────────────────────────────────
def render_paper_html(content: str, header_color: str, badge: str) -> str:
    section_colors = {"A":"#1d4ed8","B":"#d97706","C":"#059669","D":"#7c3aed","E":"#db2777"}

    # Extract SVG blocks and replace with unique placeholders
    svg_map: dict[str, str] = {}
    def _extract_svg(m):
        key = f"__SVG_{len(svg_map)}__"
        svg_map[key] = m.group(1).strip()
        return key
    processed = re.sub(r'<SVG_DIAGRAM>\s*(.*?)\s*</SVG_DIAGRAM>', _extract_svg, content, flags=re.DOTALL)

    lines = processed.splitlines()
    body = ""
    for line in lines:
        s = line.strip()
        if not s:
            body += "<div style='height:5px'></div>"
            continue

        # Inline SVG diagram
        if s in svg_map:
            svg_code = svg_map[s]
            body += (
                f'<div style="background:#f8fafc;border:1.5px solid #cbd5e1;border-radius:10px;'
                f'padding:12px;margin:12px 0;text-align:center;overflow:auto;">'
                f'{svg_code}</div>'
            )
            continue

        upper = s.upper()

        # Case study box
        if "CASE STUDY" in upper or s.startswith("─"):
            if s.startswith("─"):
                body += '<div style="border-top:1px dashed #d97706;margin:4px 0;"></div>'
            else:
                body += f'<div style="background:#fffbeb;border-left:4px solid #f59e0b;padding:10px 14px;margin:10px 0;border-radius:0 8px 8px 0;font-size:13px;font-weight:600;color:#92400e;">{s}</div>'
            continue

        # Section headings
        if any(f"SECTION {c}" in upper for c in "ABCDE"):
            ltr = next((c for c in "ABCDE" if f"SECTION {c}" in upper), "A")
            col = section_colors.get(ltr, "#1d4ed8")
            body += f'<div style="border-left:4px solid {col};background:#f8fafc;padding:8px 14px;margin:16px 0 8px;border-radius:0 6px 6px 0;font-size:13px;font-weight:700;color:#1e293b;">{s}</div>'
            continue

        # Answer key heading
        if "ANSWER KEY" in upper or "MARKING SCHEME" in upper:
            body += f'<div style="border-left:4px solid #059669;background:#f0fdf4;padding:8px 14px;margin:16px 0 8px;border-radius:0 6px 6px 0;font-size:13px;font-weight:700;color:#064e3b;">{s}</div>'
            continue

        # MCQ options line (starts with (a) or a))
        if s[:3] in ["(a)","(b)","(c)","(d)"] or (len(s) > 3 and s[1] == ")" and s[0] in "abcd"):
            body += f'<p style="font-size:12px;color:#374151;margin:1px 0 1px 20px;line-height:1.5;">{s}</p>'
            continue

        # Question lines (Q1. / 1. / Q1))
        if re.match(r'^(Q?\d+[\.\)])', s):
            body += f'<p style="font-size:13px;font-weight:500;color:#1e293b;margin:7px 0 2px;line-height:1.7;">{s}</p>'
        else:
            body += f'<p style="font-size:12.5px;color:#374151;margin:3px 0;line-height:1.65;">{s}</p>'

    return f"""<div style="background:white;border-radius:14px;overflow:hidden;
        box-shadow:0 8px 40px rgba(0,0,0,.3);margin-bottom:16px;">
      <div style="background:{header_color};padding:10px 20px;display:flex;align-items:center;gap:10px;">
        <span style="color:white;font-weight:600;font-size:13px;">{badge}</span>
        <span style="color:rgba(255,255,255,.55);font-size:11px;">
          {subject} · {grade} · {board} · {total_marks} marks · {duration}
        </span>
      </div>
      <div style="padding:24px 32px;font-family:Georgia,serif;">{body}</div>
    </div>"""


# ── Generation ────────────────────────────────────────────────────────────────
if generate_btn:
    if not all([subject, board, topics]):
        st.error("Please fill in Subject, Board and Topics.")
        st.stop()
    if not selected_types:
        st.error("Please select at least one question type.")
        st.stop()

    # Strip ★ prefix for prompt
    clean_types = [t.replace("★ ", "") for t in selected_types]

    spinner_msg = f"⏳ Generating with {model_label}…"
    with st.spinner(spinner_msg):
        try:
            prompt = build_paper_prompt(
                subject=subject, grade=grade, board=board, topics=topics,
                num_questions=int(num_questions), difficulty=difficulty,
                total_marks=int(total_marks), duration=duration,
                question_types=clean_types,
                special_instructions=special,
            )
            raw_output = model_caller(prompt)
        except Exception as e:
            err = str(e)
            if "429" in err or "quota" in err.lower():
                st.error(f"Quota exceeded for {model_label}. The app will use the next available model on retry.")
            elif "credit" in err.lower() or "billing" in err.lower():
                st.error(f"Billing issue with {model_label}. Add credits or switch to a free model.")
            else:
                st.error(f"Generation failed: {e}")
            st.stop()

    # Split output
    if "==ANSWER SHEET==" in raw_output:
        parts       = raw_output.split("==ANSWER SHEET==")
        paper_text  = parts[0].replace("==QUESTION PAPER==", "").strip()
        answer_text = parts[1].strip()
    else:
        paper_text  = raw_output.strip()
        answer_text = "_Answer sheet not returned. Please regenerate._"

    st.success(f"✓ Generated by {model_label}")

    # ── Output tabs ───────────────────────────────────────────────────────────
    tab_q, tab_a = st.tabs(["📄  Question Paper", "✅  Answer Sheet & Marking Scheme"])

    with tab_q:
        st.markdown(render_paper_html(paper_text, "#1e3a5f", "📄 Question Paper"), unsafe_allow_html=True)
        docx_q = generate_docx(paper_text, subject, grade, board, int(total_marks), duration)
        st.download_button("⬇  Download Question Paper (.docx)", data=docx_q,
            file_name=f"{subject.replace(' ','_')}_{grade.replace(' ','_')}_question_paper.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    with tab_a:
        st.markdown(render_paper_html(answer_text, "#14532d", "✅ Answer Sheet & Marking Scheme"), unsafe_allow_html=True)
        docx_a = generate_docx(answer_text, f"{subject} — Answer Key", grade, board, int(total_marks), duration)
        st.download_button("⬇  Download Answer Sheet (.docx)", data=docx_a,
            file_name=f"{subject.replace(' ','_')}_{grade.replace(' ','_')}_answer_sheet.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# ── Empty state ───────────────────────────────────────────────────────────────
else:
    st.markdown(f"""
    <div style="text-align:center;padding:44px 24px;">
      <div style="font-size:44px;margin-bottom:14px;">📝</div>
      <h2 style="font-size:21px;font-weight:600;color:#f1f5f9;margin-bottom:8px;">Ready to Generate</h2>
      <p style="font-size:13px;color:#64748b;max-width:480px;margin:0 auto 32px;line-height:1.75;">
        Fill in the paper details on the left and click
        <strong style="color:#60a5fa;">Generate Paper + Answer Sheet</strong>.
        The app automatically uses the best available free model.
      </p>

      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;max-width:560px;margin:0 auto 28px;">
        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:14px;text-align:left;">
          <div style="font-size:20px;margin-bottom:6px;">📖</div>
          <div style="font-size:12px;font-weight:600;color:#f1f5f9;margin-bottom:2px;">Case Study MCQ</div>
          <div style="font-size:10px;color:#64748b;line-height:1.5;">Passage + questions that test reading comprehension</div>
        </div>
        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:14px;text-align:left;">
          <div style="font-size:20px;margin-bottom:6px;">🖼️</div>
          <div style="font-size:12px;font-weight:600;color:#f1f5f9;margin-bottom:2px;">Picture-Based MCQ</div>
          <div style="font-size:10px;color:#64748b;line-height:1.5;">Diagram description + visual MCQs</div>
        </div>
        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:14px;text-align:left;">
          <div style="font-size:20px;margin-bottom:6px;">✏️</div>
          <div style="font-size:12px;font-weight:600;color:#f1f5f9;margin-bottom:2px;">Picture Fill-in-Blank</div>
          <div style="font-size:10px;color:#64748b;line-height:1.5;">Diagram with blanks to label or complete</div>
        </div>
      </div>

      <div style="display:inline-flex;align-items:center;gap:8px;background:#0f172a;
          border:1px solid #1e293b;border-radius:10px;padding:10px 18px;">
        <span style="width:7px;height:7px;border-radius:50%;background:#10b981;display:inline-block;"></span>
        <span style="font-size:12px;color:#94a3b8;">Using: <strong style="color:#e2e8f0;">{model_label}</strong></span>
      </div>
    </div>
    """, unsafe_allow_html=True)
