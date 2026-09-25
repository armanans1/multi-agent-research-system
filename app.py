"""
Multi-Agent Research System — Streamlit Frontend
--------------------------------------------------
Reuses the existing backend `run_research_pipeline(topic)` from pipeline.py.
Does NOT modify agents.py / tools.py. Only reads the dict this function
already returns:

    {
        "search_results": str,
        "scraped_content": str,
        "report": str,
        "feedback": str,
    }

Run with:
    streamlit run app.py
"""

import os
import re
import time
import traceback
import streamlit as st

# --- Backend import (unchanged) --------------------------------------------
from pipeline import run_research_pipeline

# Optional: only used to *check* (not print) whether keys are configured.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Multi-Agent Research System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# CUSTOM CSS — premium SaaS look
# =============================================================================
st.markdown(
    """
    <style>
        /* ---- General layout ---- */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }

        /* ---- Header ---- */
        .hero {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
            padding: 2.2rem 2.5rem;
            border-radius: 20px;
            margin-bottom: 1.8rem;
            box-shadow: 0 10px 30px rgba(99, 102, 241, 0.25);
        }
        .hero h1 {
            color: white;
            font-size: 2.1rem;
            font-weight: 800;
            margin: 0 0 0.4rem 0;
            letter-spacing: -0.02em;
        }
        .hero p {
            color: rgba(255,255,255,0.9);
            font-size: 1.02rem;
            margin: 0;
            font-weight: 400;
        }

        /* ---- Cards ---- */
        .card {
            background: var(--background-color, #ffffff10);
            border: 1px solid rgba(128,128,128,0.18);
            border-radius: 16px;
            padding: 1.25rem 1.4rem;
            margin-bottom: 0.9rem;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        }

        /* ---- Sidebar agent cards ---- */
        .agent-card {
            border-radius: 14px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.7rem;
            background: linear-gradient(145deg, rgba(99,102,241,0.08), rgba(236,72,153,0.06));
            border: 1px solid rgba(99,102,241,0.18);
        }
        .agent-card .agent-title {
            font-weight: 700;
            font-size: 0.95rem;
            margin-bottom: 0.15rem;
        }
        .agent-card .agent-desc {
            font-size: 0.82rem;
            opacity: 0.75;
            line-height: 1.3;
        }

        /* ---- Section divider ---- */
        .section-title {
            font-size: 1.1rem;
            font-weight: 700;
            margin: 1.2rem 0 0.6rem 0;
            padding-bottom: 0.4rem;
            border-bottom: 2px solid rgba(99,102,241,0.25);
        }

        /* ---- Buttons ---- */
        .stButton > button {
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: white;
            font-weight: 700;
            font-size: 1.02rem;
            border: none;
            border-radius: 12px;
            padding: 0.7rem 1.4rem;
            width: 100%;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            box-shadow: 0 6px 16px rgba(99,102,241,0.30);
        }
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 10px 22px rgba(99,102,241,0.40);
        }

        /* ---- Source link chips ---- */
        .source-link {
            display: block;
            padding: 0.55rem 0.9rem;
            margin-bottom: 0.5rem;
            border-radius: 10px;
            background: rgba(99,102,241,0.07);
            border: 1px solid rgba(99,102,241,0.15);
            text-decoration: none;
            font-size: 0.88rem;
            word-break: break-all;
        }
        .source-link:hover {
            background: rgba(99,102,241,0.14);
        }

        /* ---- Report container ---- */
        .report-box {
            background: rgba(128,128,128,0.05);
            border: 1px solid rgba(128,128,128,0.15);
            border-radius: 16px;
            padding: 1.6rem 1.8rem;
            line-height: 1.65;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# HELPERS
# =============================================================================
def to_text(value) -> str:
    """
    Normalize whatever the backend returns (plain str, LangChain AIMessage,
    dict with 'content', etc.) into a plain string for display.
    Safe no-op if it's already a string.
    """
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    # LangChain message objects expose `.content`
    content = getattr(value, "content", None)
    if content is not None:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict) and "text" in item:
                    parts.append(item["text"])
                else:
                    parts.append(str(item))
            return "\n".join(parts)
    if isinstance(value, dict):
        # common patterns: {"text": ...} or {"output": ...}
        for key in ("text", "output", "content"):
            if key in value:
                return to_text(value[key])
        return str(value)
    return str(value)


def extract_urls(*texts) -> list[str]:
    """Pull unique URLs out of one or more blocks of text, preserving order."""
    url_pattern = re.compile(r"https?://[^\s\)\]\}\"'>]+")
    seen = set()
    urls = []
    for text in texts:
        for match in url_pattern.findall(text or ""):
            cleaned = match.rstrip(".,;:")
            if cleaned not in seen:
                seen.add(cleaned)
                urls.append(cleaned)
    return urls


def extract_score(feedback_text: str):
    """Best-effort extraction of a numeric score like 'Score: 8/10' from feedback."""
    match = re.search(r"score[:\s]*([0-9]{1,2})\s*(?:/|out of)\s*10", feedback_text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    match = re.search(r"score[:\s]*([0-9]{1,3})", feedback_text, re.IGNORECASE)
    if match:
        val = int(match.group(1))
        if val <= 10:
            return val
    return None


def split_feedback_sections(feedback_text: str) -> dict:
    """
    Best-effort split of critic feedback into Strengths / Areas to Improve /
    Final Verdict sections, based on common heading patterns. Falls back to
    putting everything under 'Full Review' if headings aren't found.
    """
    headings = {
        "strengths": r"(strengths?|pros|what.?s good)",
        "improve": r"(areas? to improve|weaknesses?|cons|what could be better)",
        "verdict": r"(final verdict|conclusion|overall|summary)",
    }
    sections = {}
    text = feedback_text or ""

    pattern = re.compile(
        r"(?im)^\s*#{0,3}\s*(" + "|".join(headings.values()) + r")\s*[:\-]?\s*$"
    )
    matches = list(pattern.finditer(text))

    if not matches:
        return {"full": text}

    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        label = m.group(1).lower()
        chunk = text[start:end].strip()
        if re.search(headings["strengths"], label, re.IGNORECASE):
            sections["strengths"] = chunk
        elif re.search(headings["improve"], label, re.IGNORECASE):
            sections["improve"] = chunk
        elif re.search(headings["verdict"], label, re.IGNORECASE):
            sections["verdict"] = chunk

    leading = text[: matches[0].start()].strip()
    if leading:
        sections["intro"] = leading

    return sections if sections else {"full": text}


def friendly_error_message(exc: Exception) -> str:
    msg = str(exc)
    lower = msg.lower()

    if "429" in msg or "resource_exhausted" in lower or "quota" in lower:
        return "⚠️ AI model quota has been reached. Please wait and try again later."
    if "api key" in lower or "authentication" in lower or "unauthorized" in lower:
        return "⚠️ A required API key is missing or invalid. Please check your `.env` file."
    if "tavily" in lower:
        return "⚠️ The search provider (Tavily) returned an error. Please try again shortly."
    if "connection" in lower or "timeout" in lower or "network" in lower:
        return "⚠️ A network error occurred while contacting an external service. Please check your connection and try again."
    return "⚠️ Something went wrong while running the research pipeline. Please try again."


def check_env_keys() -> list[str]:
    """Return a list of missing expected env var names, without printing values."""
    expected = ["GOOGLE_API_KEY", "GEMINI_API_KEY", "TAVILY_API_KEY"]
    # Consider it "configured" if at least one Gemini-style key + Tavily key exist.
    missing = []
    has_gemini_key = bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))
    has_tavily_key = bool(os.getenv("TAVILY_API_KEY"))
    if not has_gemini_key:
        missing.append("GOOGLE_API_KEY / GEMINI_API_KEY")
    if not has_tavily_key:
        missing.append("TAVILY_API_KEY")
    return missing


# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown("### 🧠 The Agent Team")

    agents = [
        ("🔍", "Search Agent", "Finds reliable and recent information"),
        ("📖", "Reader Agent", "Reads and analyzes useful sources"),
        ("✍️", "Writer Agent", "Creates a structured research report"),
        ("🧐", "Critic Agent", "Reviews and evaluates the report"),
    ]
    for icon, title, desc in agents:
        st.markdown(
            f"""
            <div class="agent-card">
                <div class="agent-title">{icon} {title}</div>
                <div class="agent-desc">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    missing_keys = check_env_keys()
    if missing_keys:
        st.warning("Missing configuration:\n" + "\n".join(f"- {k}" for k in missing_keys))
    else:
        st.success("API keys detected ✅")

    st.markdown("---")
    st.caption("Built with LangChain, Gemini and Tavily.")


# =============================================================================
# HEADER
# =============================================================================
st.markdown(
    """
    <div class="hero">
        <h1>🤖 Multi-Agent Research System</h1>
        <p>AI-powered research using Search, Reader, Writer and Critic agents</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# SESSION STATE
# =============================================================================
if "result" not in st.session_state:
    st.session_state.result = None
if "last_topic" not in st.session_state:
    st.session_state.last_topic = ""


# =============================================================================
# MAIN INPUT
# =============================================================================
st.markdown('<div class="section-title">Start a new research task</div>', unsafe_allow_html=True)

topic = st.text_input(
    "Enter your research topic",
    placeholder="e.g. What are the next big jobs in Artificial Intelligence?",
)

start = st.button("🚀 Start Research", use_container_width=True)


# =============================================================================
# RUN PIPELINE
# =============================================================================
if start:
    if not topic or not topic.strip():
        st.error("⚠️ Please enter a research topic before starting.")
    elif missing_keys:
        st.error("⚠️ Cannot start: required API keys are missing. Check the sidebar for details.")
    else:
        stage_labels = [
            "🔍 Searching the web",
            "📖 Reading sources",
            "✍️ Writing research report",
            "🧐 Critic reviewing report",
        ]

        with st.status("Running the research pipeline...", expanded=True) as status:
            for label in stage_labels:
                st.write(label)

            try:
                result = run_research_pipeline(topic.strip())
                st.session_state.result = result
                st.session_state.last_topic = topic.strip()
                status.update(label="✅ Research complete!", state="complete", expanded=False)
            except Exception as exc:  # noqa: BLE001
                status.update(label="❌ Research failed", state="error", expanded=True)
                st.error(friendly_error_message(exc))
                with st.expander("Technical details (for debugging)"):
                    st.code(traceback.format_exc())
                st.session_state.result = None


# =============================================================================
# RESULTS
# =============================================================================
if st.session_state.result:
    result = st.session_state.result

    report_text = to_text(result.get("report"))
    feedback_text = to_text(result.get("feedback"))
    search_text = to_text(result.get("search_results"))
    scraped_text = to_text(result.get("scraped_content"))

    st.markdown('<div class="section-title">Results</div>', unsafe_allow_html=True)
    st.caption(f"Topic: **{st.session_state.last_topic}**")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📄 Research Report", "🔗 Sources", "🧐 Critic Review", "🗂️ Raw Research Data"]
    )

    # --- Tab 1: Report ---
    with tab1:
        if report_text:
            st.markdown(f'<div class="report-box">{report_text}</div>', unsafe_allow_html=True)
        else:
            st.info("No report was generated.")

    # --- Tab 2: Sources ---
    with tab2:
        urls = extract_urls(search_text, scraped_text, report_text)
        if urls:
            st.write(f"Found **{len(urls)}** source link(s):")
            for url in urls:
                st.markdown(
                    f'<a class="source-link" href="{url}" target="_blank">🔗 {url}</a>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No URLs were found in the research output.")

    # --- Tab 3: Critic Review ---
    with tab3:
        score = extract_score(feedback_text)
        if score is not None:
            st.metric("Critic Score", f"{score} / 10")

        sections = split_feedback_sections(feedback_text)

        if "full" in sections:
            st.markdown(f'<div class="card">{sections["full"]}</div>', unsafe_allow_html=True)
        else:
            if "intro" in sections:
                st.markdown(f'<div class="card">{sections["intro"]}</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**✅ Strengths**")
                st.markdown(
                    f'<div class="card">{sections.get("strengths", "Not specified.")}</div>',
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown("**🛠️ Areas to Improve**")
                st.markdown(
                    f'<div class="card">{sections.get("improve", "Not specified.")}</div>',
                    unsafe_allow_html=True,
                )

            if "verdict" in sections:
                st.markdown("**🏁 Final Verdict**")
                st.markdown(f'<div class="card">{sections["verdict"]}</div>', unsafe_allow_html=True)

        with st.expander("View raw critic feedback"):
            st.text(feedback_text)

    # --- Tab 4: Raw Research Data ---
    with tab4:
        with st.expander("🔍 Search Agent Results", expanded=True):
            st.text(search_text or "No data.")
        with st.expander("📖 Scraped Content"):
            st.text(scraped_text or "No data.")

else:
    st.markdown(
        """
        <div class="card" style="text-align:center; padding: 2.5rem 1rem;">
            <p style="font-size:1.05rem; opacity:0.75; margin:0;">
                Enter a topic above and click <b>Start Research</b> to see results here.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
