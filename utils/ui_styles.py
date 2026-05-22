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

    # Upload section — explicit light/dark (overrides Streamlit default theme)
    upload_zone_bg = "rgba(30,41,59,0.55)" if dark else "#ffffff"
    upload_zone_border = "rgba(129,140,248,0.45)" if dark else "#cbd5e1"
    upload_zone_text = "#e2e8f0" if dark else "#334155"
    upload_zone_title = "#f8fafc" if dark else "#0f172a"
    upload_zone_shadow = "0 4px 24px rgba(0,0,0,0.25)" if dark else "0 2px 14px rgba(15,23,42,0.08)"
    upload_drop_bg = "rgba(15,23,42,0.5)" if dark else "#f8fafc"
    upload_drop_border = "rgba(148,163,184,0.35)" if dark else "#94a3b8"
    upload_drop_hover = "rgba(30,41,59,0.7)" if dark else "#eef2ff"
    upload_btn_bg = "rgba(51,65,85,0.9)" if dark else "#ffffff"
    upload_btn_text = "#f1f5f9" if dark else "#1e293b"
    upload_btn_border = "rgba(148,163,184,0.4)" if dark else "#cbd5e1"
    upload_icon = "#a5b4fc" if dark else "#6366f1"
    upload_chip_bg = "rgba(30,41,59,0.55)" if dark else "rgba(255,255,255,0.95)"
    upload_chip_border = "rgba(129,140,248,0.35)" if dark else "#e2e8f0"
    upload_chip_hover = "rgba(51,65,85,0.75)" if dark else "#f1f5f9"

    # Sidebar brand
    brand_title = "#f8fafc" if dark else "#0f172a"
    brand_sub = "#cbd5e1" if dark else "#475569"
    brand_title_glow = (
        "0 0 20px rgba(129,140,248,0.55), 0 0 40px rgba(34,211,238,0.15)"
        if dark
        else "none"
    )
    brand_title_grad = (
        "linear-gradient(135deg, #f8fafc 0%, #c7d2fe 50%, #67e8f9 100%)"
        if dark
        else "linear-gradient(135deg, #0f172a 0%, #4338ca 55%, #0284c7 100%)"
    )

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

/* ── Sidebar brand (Ask My Docs) ── */
.sidebar-brand {{
    text-align: center !important;
    padding: 0.5rem 0.5rem 0.9rem !important;
    margin-bottom: 0.25rem !important;
}}
.sidebar-brand-icon {{
    font-size: 1.5rem !important;
    line-height: 1.2 !important;
    display: block !important;
    margin-bottom: 0.35rem !important;
    filter: {"drop-shadow(0 0 8px rgba(129,140,248,0.5))" if dark else "none"} !important;
}}
.sidebar-brand-title {{
    font-weight: 800 !important;
    font-size: 1.08rem !important;
    line-height: 1.3 !important;
    margin: 0 !important;
    padding: 0 !important;
    color: {brand_title} !important;
    -webkit-text-fill-color: {brand_title} !important;
    background: {brand_title_grad} !important;
    -webkit-background-clip: text !important;
    background-clip: text !important;
    filter: {"drop-shadow(0 0 12px rgba(129,140,248,0.45))" if dark else "none"} !important;
    letter-spacing: -0.02em !important;
}}
.sidebar-brand-sub {{
    font-size: 0.78rem !important;
    line-height: 1.4 !important;
    margin: 0.35rem 0 0 0 !important;
    padding: 0 !important;
    color: {brand_sub} !important;
    opacity: 1 !important;
}}
section[data-testid="stSidebar"] .sidebar-brand-title {{
    color: {brand_title} !important;
    -webkit-text-fill-color: {brand_title} !important;
}}
section[data-testid="stSidebar"] .sidebar-brand-sub {{
    color: {brand_sub} !important;
    opacity: 1 !important;
}}
section[data-testid="stSidebar"] div[data-testid="stHtml"] .sidebar-brand * {{
    opacity: 1 !important;
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

/* ── Upload zone hint card (custom HTML) ── */
.upload-zone {{
    border: 2px dashed {upload_zone_border} !important;
    border-radius: 14px !important;
    padding: 0.85rem !important;
    text-align: center !important;
    background: {upload_zone_bg} !important;
    margin-bottom: 0.65rem !important;
    box-shadow: {upload_zone_shadow} !important;
}}
.upload-zone p {{
    margin: 0 !important;
    font-size: 0.82rem !important;
}}
.upload-zone-title,
.upload-zone-title strong {{
    color: {upload_zone_title} !important;
    font-weight: 700 !important;
}}
.upload-zone-sub {{
    color: {upload_zone_text} !important;
}}

/* ── Streamlit file uploader (sidebar) ── */
section[data-testid="stSidebar"] [data-testid="stFileUploader"],
section[data-testid="stSidebar"] .stFileUploader {{
    background: transparent !important;
    border-radius: 12px !important;
    width: 100% !important;
    max-width: 100% !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
}}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] > div,
section[data-testid="stSidebar"] .stFileUploader > div {{
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
}}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] section[data-testid="stFileUploader"] {{
    width: 100% !important;
    max-width: 100% !important;
    padding: 0 !important;
}}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {{
    background: {upload_drop_bg} !important;
    border: 2px dashed {upload_drop_border} !important;
    border-radius: 14px !important;
    box-shadow: {upload_zone_shadow} !important;
    padding: 0.75rem 0.65rem !important;
    min-height: 120px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: stretch !important;
    justify-content: flex-start !important;
    text-align: left !important;
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
    gap: 0.45rem !important;
}}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"]:hover {{
    background: {upload_drop_hover} !important;
    border-color: {accent} !important;
}}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] > div {{
    background: transparent !important;
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: stretch !important;
    justify-content: flex-start !important;
    text-align: left !important;
    gap: 0.4rem !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
}}
/* File list — stFileChips container */
section[data-testid="stSidebar"] [data-testid="stFileChips"] {{
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    flex-wrap: nowrap !important;
    align-items: stretch !important;
    gap: 0.4rem !important;
    overflow-x: hidden !important;
    overflow-y: auto !important;
    max-height: 12rem !important;
    box-sizing: border-box !important;
}}
section[data-testid="stSidebar"] [data-testid="stFileChips"] > div {{
    display: flex !important;
    flex-direction: column !important;
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    gap: 0.35rem !important;
    align-items: stretch !important;
}}
section[data-testid="stSidebar"] [data-testid="stFileChips"] > div > div {{
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    flex: 0 0 auto !important;
}}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] {{
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    width: 100% !important;
    margin: 0 auto !important;
    padding: 0.25rem 0 0 0 !important;
}}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] > div,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] div {{
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    width: 100% !important;
    margin: 0 auto !important;
}}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] span,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] p,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] label {{
    color: {upload_zone_text} !important;
    text-align: center !important;
    width: 100% !important;
    display: block !important;
    margin-left: auto !important;
    margin-right: auto !important;
    line-height: 1.45 !important;
}}
/* Upload / Add button row (empty or with files) */
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] > div > button,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button[kind="secondary"],
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] [data-testid="baseButton-secondary"] {{
    background: {upload_btn_bg} !important;
    color: {upload_btn_text} !important;
    border: 1px solid {upload_btn_border} !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    flex-shrink: 0 !important;
    align-self: center !important;
    margin: 0.25rem auto !important;
    width: auto !important;
    max-width: calc(100% - 1rem) !important;
    min-width: unset !important;
}}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button:hover {{
    background: {upload_drop_hover} !important;
    color: {upload_btn_text} !important;
    border-color: {accent} !important;
}}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button p,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button span {{
    color: {upload_btn_text} !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
}}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] svg {{
    fill: {upload_icon} !important;
    color: {upload_icon} !important;
    flex-shrink: 0 !important;
}}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] {{
    width: 100% !important;
    max-width: 100% !important;
}}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] p {{
    color: {upload_zone_text} !important;
}}

/* ── Uploaded file chips (stFileChip inside dropzone) ── */
section[data-testid="stSidebar"] [data-testid="stFileChip"] {{
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: 0.45rem !important;
    padding: 0.5rem 0.6rem !important;
    margin: 0 !important;
    background: {upload_chip_bg} !important;
    backdrop-filter: blur(8px) !important;
    -webkit-backdrop-filter: blur(8px) !important;
    border: 1px solid {upload_chip_border} !important;
    border-radius: 10px !important;
    box-shadow: {"0 2px 8px rgba(0,0,0,0.2)" if dark else "0 1px 4px rgba(15,23,42,0.06)"} !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
    flex-shrink: 0 !important;
    cursor: default !important;
}}
section[data-testid="stSidebar"] [data-testid="stFileChip"]:hover {{
    background: {upload_chip_hover} !important;
    border-color: {accent} !important;
}}
/* Icon column */
section[data-testid="stSidebar"] [data-testid="stFileChip"] > div:first-child {{
    flex-shrink: 0 !important;
}}
/* Filename + size column */
section[data-testid="stSidebar"] [data-testid="stFileChip"] > div:nth-child(2) {{
    flex: 1 1 auto !important;
    min-width: 0 !important;
    max-width: 100% !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
}}
section[data-testid="stSidebar"] [data-testid="stFileChipName"] {{
    color: {text} !important;
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
    display: block !important;
    line-height: 1.35 !important;
}}
section[data-testid="stSidebar"] [data-testid="stFileChip"] > div:nth-child(2) > div:last-child {{
    color: {muted} !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
    max-width: 100% !important;
}}
/* Remove / delete button */
section[data-testid="stSidebar"] [data-testid="stFileChipDeleteBtn"] {{
    flex: 0 0 auto !important;
    flex-shrink: 0 !important;
    align-self: center !important;
    margin: 0 !important;
}}
section[data-testid="stSidebar"] [data-testid="stFileChipDeleteBtn"] button {{
    flex-shrink: 0 !important;
    margin: 0 !important;
    padding: 0.25rem !important;
    min-width: 2rem !important;
    width: 2rem !important;
    height: 2rem !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}}
section[data-testid="stSidebar"] [data-testid="stFileChipDeleteBtn"] button:hover {{
    background: {upload_drop_hover} !important;
    border-radius: 6px !important;
}}
/* Trailing "Add files" icon button */
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] [data-testid="baseButton-borderlessIcon"],
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button[kind="borderlessIcon"] {{
    flex-shrink: 0 !important;
    align-self: flex-end !important;
    margin: 0.15rem 0 0 auto !important;
}}
section[data-testid="stSidebar"] .uploadedFile {{
    background: {upload_chip_bg} !important;
    color: {text} !important;
    max-width: 100% !important;
    overflow: hidden !important;
}}

/* Sidebar width guard on narrow viewports */
section[data-testid="stSidebar"] {{
    overflow-x: hidden !important;
}}
section[data-testid="stSidebar"] > div {{
    overflow-x: hidden !important;
    max-width: 100% !important;
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
