"""Premium light/dark theme CSS for Ask My Docs — full Streamlit widget coverage."""


def get_theme_css(theme: str) -> str:
    dark = theme == "dark"

    # Palette
    bg = "#0a0e17" if dark else "#f1f5f9"
    bg2 = "#111827" if dark else "#ffffff"
    bg3 = "#1a2234" if dark else "#ffffff"
    text = "#f1f5f9" if dark else "#0f172a"
    text2 = "#cbd5e1" if dark else "#475569"
    muted = "#94a3b8" if dark else "#64748b"
    card = "rgba(30,41,59,0.65)" if dark else "rgba(255,255,255,0.92)"
    border = "rgba(148,163,184,0.22)" if dark else "rgba(15,23,42,0.1)"
    accent = "#818cf8" if dark else "#4f46e5"
    accent2 = "#22d3ee" if dark else "#0284c7"
    glow = "rgba(99,102,241,0.4)" if dark else "rgba(79,70,229,0.2)"
    input_bg = "#1e293b" if dark else "#ffffff"
    hero_grad = (
        "linear-gradient(135deg,#0c1222 0%,#1e1b4b 40%,#312e81 75%,#0c4a6e 100%)"
        if dark
        else "linear-gradient(135deg,#eef2ff 0%,#e0e7ff 45%,#dbeafe 80%,#ecfeff 100%)"
    )
    hero_title = "#f8fafc" if dark else "#0f172a"
    hero_sub = "#cbd5e1" if dark else "#475569"
    stat_value_color = "#a5b4fc" if dark else "#4338ca"

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Base app ── */
.stApp {{
    background: {bg} !important;
    color: {text} !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}}

.main, .block-container {{
    color: {text} !important;
}}

.block-container {{
    padding-top: 1rem;
    max-width: 1120px;
}}

/* All primary text in main area */
.stApp p, .stApp span, .stApp label, .stApp li,
.stApp h1, .stApp h2, .stApp h3, .stApp h4,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stCaptionContainer"] p {{
    color: {text} !important;
}}

[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {{
    color: {text} !important;
}}

/* Sidebar */
section[data-testid="stSidebar"] > div {{
    background: {bg2} !important;
    border-right: 1px solid {border} !important;
}}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
    color: {text} !important;
}}

section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
    color: {muted} !important;
}}

/* Metrics */
[data-testid="stMetric"] {{
    background: {card} !important;
    border: 1px solid {border} !important;
    border-radius: 12px !important;
    padding: 0.65rem 0.75rem !important;
}}
[data-testid="stMetricLabel"] {{
    color: {muted} !important;
}}
[data-testid="stMetricValue"] {{
    color: {text} !important;
}}

/* Buttons */
.stButton > button {{
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}}
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, {accent}, {accent2}) !important;
    color: #fff !important;
    border: none !important;
    box-shadow: 0 4px 20px {glow} !important;
}}
.stButton > button[kind="primary"]:hover {{
    box-shadow: 0 6px 28px {glow} !important;
    transform: translateY(-1px);
}}
.stButton > button[kind="secondary"] {{
    background: {card} !important;
    color: {text} !important;
    border: 1px solid {border} !important;
}}

/* Inputs & chat */
.stTextInput input, .stTextArea textarea,
[data-testid="stChatInput"] textarea {{
    background: {input_bg} !important;
    color: {text} !important;
    border: 1px solid {border} !important;
    border-radius: 12px !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{
    color: {muted} !important;
}}

/* File uploader */
[data-testid="stFileUploader"] {{
    background: {card} !important;
    border-radius: 12px !important;
}}
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] small {{
    color: {text2} !important;
}}

/* Expanders (sources) */
.streamlit-expanderHeader {{
    background: {card} !important;
    color: {text} !important;
    border-radius: 10px !important;
}}
details {{
    border: 1px solid {border} !important;
    border-radius: 10px !important;
    background: {bg3} !important;
}}

/* Chat messages */
[data-testid="stChatMessage"] {{
    background: transparent !important;
    animation: fadeIn 0.35s ease;
}}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {{
    color: {text} !important;
}}

/* Alerts */
.stAlert {{
    border-radius: 12px !important;
}}
div[data-testid="stNotification"] {{
    color: {text} !important;
}}

/* Status widget */
[data-testid="stStatusWidget"] {{
    color: {text} !important;
}}

/* Toggle */
.stCheckbox label, .stToggle label {{
    color: {text} !important;
}}

/* Code blocks */
.stCode, pre {{
    background: {"#0f172a" if dark else "#f8fafc"} !important;
    color: {text2} !important;
}}

/* Hide chrome */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header[data-testid="stHeader"] {{
    background: transparent !important;
}}

::-webkit-scrollbar {{ width: 8px; }}
::-webkit-scrollbar-thumb {{
    background: {muted};
    border-radius: 8px;
}}

/* ── Hero ── */
.hero-wrap {{
    border-radius: 20px;
    padding: 1.75rem 2rem;
    margin-bottom: 0.5rem;
    background: {hero_grad};
    border: 1px solid {border};
    box-shadow: 0 16px 48px {glow};
    overflow: hidden;
    animation: fadeIn 0.5s ease;
}}
.hero-wrap--lottie {{
    padding: 0.75rem 1rem;
    margin-bottom: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 0;
}}

/* Lottie container (Streamlit bordered box) */
[data-testid="stVerticalBlockBorderWrapper"] {{
    border-color: {border} !important;
    background: {card} !important;
    border-radius: 16px !important;
}}
.hero-title {{
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin: 0 0 0.45rem 0;
    color: {hero_title} !important;
}}
.hero-sub {{
    font-size: 1rem;
    line-height: 1.55;
    color: {hero_sub} !important;
    margin: 0 0 0.85rem 0;
}}
.hero-tags {{ display: flex; flex-wrap: wrap; gap: 0.45rem; }}
.hero-tag {{
    font-size: 0.72rem;
    padding: 0.3rem 0.65rem;
    border-radius: 999px;
    background: {card};
    border: 1px solid {border};
    color: {text2} !important;
}}

/* Lottie column — no extra empty box */
.lottie-wrap {{
    margin: 0;
    padding: 0;
    line-height: 0;
}}
.lottie-wrap iframe {{
    border: none !important;
}}

/* Stat cards */
.stat-card {{
    background: {card};
    backdrop-filter: blur(12px);
    border: 1px solid {border};
    border-radius: 16px;
    padding: 1rem 1.15rem;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    animation: fadeIn 0.45s ease;
    margin-bottom: 0.25rem;
}}
.stat-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 12px 28px {glow};
}}
.stat-icon {{ font-size: 1.35rem; margin-bottom: 0.3rem; }}
.stat-value {{
    font-size: 1.55rem;
    font-weight: 800;
    color: {stat_value_color} !important;
    -webkit-text-fill-color: {stat_value_color} !important;
}}
.stat-label {{
    font-size: 0.78rem;
    color: {muted} !important;
    margin-top: 0.15rem;
    font-weight: 500;
}}

/* Badges & footer */
.badge-row {{ display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 0.5rem; }}
.badge {{
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.2rem 0.55rem;
    border-radius: 6px;
    background: linear-gradient(90deg, {accent}33, {accent2}33);
    border: 1px solid {border};
    color: {text} !important;
}}
.upload-zone {{
    border: 2px dashed {border};
    border-radius: 14px;
    padding: 0.85rem;
    text-align: center;
    background: {card};
    margin-bottom: 0.65rem;
}}
.upload-zone p {{
    margin: 0;
    color: {text2} !important;
    font-size: 0.82rem;
}}
.app-footer {{
    text-align: center;
    padding: 1.75rem 0 0.75rem;
    color: {muted} !important;
    font-size: 0.85rem;
}}
.app-footer strong {{
    color: {text2} !important;
}}

/* Remove empty stHtml boxes */
div[data-testid="stHtml"]:empty {{
    display: none !important;
    min-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}}

@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(6px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

@media (max-width: 768px) {{
    .hero-title {{ font-size: 1.65rem; }}
    .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
}}
</style>
"""
