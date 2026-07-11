import streamlit as st
import httpx
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Travel Planner • Multi-Agent System",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    /* ── Root Variables ── */
    :root {
        --bg-main:        #070B14;
        --bg-card:        rgba(255,255,255,0.04);
        --bg-card-hover:  rgba(255,255,255,0.07);
        --border:         rgba(255,255,255,0.08);
        --border-bright:  rgba(255,255,255,0.14);
        --text-primary:   #F0F4FF;
        --text-secondary: #94A3B8;
        --text-muted:     #475569;
        --accent-blue:    #3B82F6;
        --accent-cyan:    #06B6D4;
        --accent-violet:  #7C3AED;
        --accent-pink:    #EC4899;
        --accent-amber:   #F59E0B;
        --accent-emerald: #10B981;
        --accent-red:     #EF4444;
        --glow-blue:      rgba(59,130,246,0.25);
        --glow-violet:    rgba(124,58,237,0.20);
    }

    /* ── Base Reset ── */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: var(--bg-main) !important;
        color: var(--text-primary) !important;
    }
    .main .block-container { padding: 2rem 2.5rem 3rem; max-width: 1400px; }
    h1,h2,h3,h4,h5 { font-family: 'Plus Jakarta Sans', sans-serif !important; }

    /* Hide default Streamlit elements */
    #MainMenu, footer, header { visibility: hidden; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--border-bright); border-radius: 99px; }

    /* ─────────────────────────────────────────────
       HERO HEADER
    ───────────────────────────────────────────── */
    .hero-wrap {
        text-align: center;
        padding: 3rem 0 2.5rem;
        position: relative;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(59,130,246,0.12);
        border: 1px solid rgba(59,130,246,0.30);
        border-radius: 99px;
        padding: 5px 14px;
        font-size: 0.78rem;
        font-weight: 600;
        color: var(--accent-cyan);
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 20px;
    }
    .hero-title {
        font-size: clamp(2rem, 4vw, 3.2rem);
        font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF 0%, var(--accent-cyan) 45%, var(--accent-violet) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.15;
        letter-spacing: -0.02em;
        margin: 0 0 14px;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: var(--text-secondary);
        max-width: 560px;
        margin: 0 auto;
        line-height: 1.7;
    }
    .hero-divider {
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan));
        border-radius: 99px;
        margin: 28px auto 0;
    }

    /* ─────────────────────────────────────────────
       SIDEBAR
    ───────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D1220 0%, #070B14 100%) !important;
        border-right: 1px solid var(--border) !important;
    }
    [data-testid="stSidebar"] .block-container { padding: 1.5rem 1.2rem; }

    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 14px 0 24px;
        border-bottom: 1px solid var(--border);
        margin-bottom: 22px;
    }
    .sidebar-logo-icon {
        width: 36px; height: 36px;
        background: linear-gradient(135deg, var(--accent-blue), var(--accent-violet));
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 18px;
    }
    .sidebar-logo-text { font-size: 0.88rem; font-weight: 700; color: var(--text-primary); }
    .sidebar-logo-sub  { font-size: 0.72rem; color: var(--text-muted); }

    .sidebar-section {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--text-muted);
        margin: 20px 0 10px;
    }

    /* Streamlit form elements override */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid var(--border-bright) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    [data-testid="stSidebar"] input:focus,
    [data-testid="stSidebar"] textarea:focus {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 3px var(--glow-blue) !important;
    }
    [data-testid="stSidebar"] label {
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
    }

    /* Primary Button Override */
    [data-testid="stSidebar"] .stButton button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-violet) 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        color: #fff !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        padding: 0.65rem 1.2rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 20px var(--glow-blue) !important;
        letter-spacing: 0.02em !important;
    }
    [data-testid="stSidebar"] .stButton button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 28px rgba(59,130,246,0.45) !important;
    }

    /* ─────────────────────────────────────────────
       GLASS CARD
    ───────────────────────────────────────────── */
    .glass-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 20px 22px;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        transition: border-color 0.25s, background 0.25s;
        margin-bottom: 16px;
    }
    .glass-card:hover {
        background: var(--bg-card-hover);
        border-color: var(--border-bright);
    }
    .glass-card h4 {
        margin: 0 0 12px;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    /* ─────────────────────────────────────────────
       STAT / KPI CHIPS
    ───────────────────────────────────────────── */
    .kpi-row {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin-bottom: 28px;
    }
    .kpi-chip {
        flex: 1;
        min-width: 160px;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 16px 18px;
        transition: all 0.2s;
    }
    .kpi-chip:hover { border-color: var(--border-bright); background: var(--bg-card-hover); }
    .kpi-label { font-size: 0.72rem; font-weight: 600; color: var(--text-muted); letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px; }
    .kpi-value { font-size: 1.45rem; font-weight: 800; color: var(--text-primary); line-height: 1.2; }
    .kpi-sub   { font-size: 0.76rem; color: var(--text-secondary); margin-top: 4px; }

    /* ─────────────────────────────────────────────
       AGENT PIPELINE TRACKER
    ───────────────────────────────────────────── */
    .pipeline-wrap {
        display: flex;
        align-items: center;
        gap: 0;
        margin: 28px 0;
        overflow-x: auto;
        padding-bottom: 4px;
    }
    .pipeline-node {
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 100px;
    }
    .pipeline-icon {
        width: 44px; height: 44px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 18px;
        font-weight: 700;
        border: 2px solid;
        position: relative;
        z-index: 1;
    }
    .pipeline-icon.done   { background: rgba(16,185,129,0.15); border-color: var(--accent-emerald); color: var(--accent-emerald); }
    .pipeline-icon.active { background: rgba(59,130,246,0.18); border-color: var(--accent-blue);    color: var(--accent-blue);    animation: pulse 1.8s infinite; }
    .pipeline-icon.idle   { background: rgba(255,255,255,0.04); border-color: var(--border);       color: var(--text-muted); }
    .pipeline-label { font-size: 0.68rem; font-weight: 600; color: var(--text-secondary); margin-top: 7px; text-align: center; }
    .pipeline-connector {
        flex: 1;
        height: 2px;
        min-width: 24px;
        background: linear-gradient(90deg, var(--accent-emerald), var(--accent-blue));
        margin-bottom: 20px;
        opacity: 0.4;
    }
    @keyframes pulse { 0%,100%{box-shadow:0 0 0 0 rgba(59,130,246,0.4)} 50%{box-shadow:0 0 0 8px rgba(59,130,246,0)} }

    /* ─────────────────────────────────────────────
       LOG TERMINAL
    ───────────────────────────────────────────── */
    .terminal-wrap {
        background: #050810;
        border: 1px solid rgba(59,130,246,0.18);
        border-radius: 14px;
        overflow: hidden;
        margin-bottom: 24px;
    }
    .terminal-bar {
        background: rgba(255,255,255,0.04);
        border-bottom: 1px solid var(--border);
        padding: 10px 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .terminal-dot { width: 10px; height: 10px; border-radius: 50%; }
    .terminal-body {
        padding: 16px 18px;
        font-family: 'Fira Code', 'Cascadia Code', 'Courier New', monospace;
        font-size: 0.78rem;
        max-height: 260px;
        overflow-y: auto;
        line-height: 1.7;
    }
    .log-line { margin-bottom: 2px; }
    .log-time { color: var(--text-muted); }
    .log-tag-host { color: var(--accent-cyan);    font-weight: 700; }
    .log-tag-ok   { color: var(--accent-emerald); font-weight: 700; }
    .log-tag-err  { color: var(--accent-red);     font-weight: 700; }
    .log-msg      { color: #CBD5E1; }

    /* ─────────────────────────────────────────────
       INFO CARDS (Flight / Hotel)
    ───────────────────────────────────────────── */
    .info-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 22px;
        height: 100%;
        transition: all 0.25s;
    }
    .info-card:hover { border-color: var(--border-bright); background: var(--bg-card-hover); }
    .info-card-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 16px;
        padding-bottom: 14px;
        border-bottom: 1px solid var(--border);
    }
    .info-card-icon {
        width: 38px; height: 38px;
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 17px;
    }
    .info-card-title { font-size: 0.88rem; font-weight: 700; color: var(--text-primary); }
    .info-card-sub   { font-size: 0.72rem; color: var(--text-muted); }
    .info-row { display: flex; justify-content: space-between; align-items: flex-start; padding: 6px 0; }
    .info-label { font-size: 0.78rem; color: var(--text-muted); }
    .info-val   { font-size: 0.82rem; color: var(--text-primary); font-weight: 500; text-align: right; max-width: 60%; }
    .price-tag  { font-size: 1rem; font-weight: 800; color: var(--accent-emerald); }
    .tag-pill {
        display: inline-block;
        background: rgba(59,130,246,0.14);
        border: 1px solid rgba(59,130,246,0.25);
        border-radius: 99px;
        padding: 2px 10px;
        font-size: 0.7rem;
        font-weight: 600;
        color: var(--accent-cyan);
        margin: 2px 2px 0 0;
    }

    /* ─────────────────────────────────────────────
       DAY TABS / ITINERARY
    ───────────────────────────────────────────── */
    .day-header {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 18px 22px;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px 14px 0 0;
        border-bottom: none;
        margin-top: 20px;
    }
    .day-badge {
        background: linear-gradient(135deg, var(--accent-blue), var(--accent-violet));
        border-radius: 10px;
        padding: 6px 14px;
        font-size: 0.78rem;
        font-weight: 800;
        color: #fff;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .day-title { font-size: 1rem; font-weight: 700; color: var(--text-primary); }
    .day-route { font-size: 0.76rem; color: var(--text-muted); margin-top: 2px; }
    .day-body {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 0 0 14px 14px;
        padding: 16px 20px 20px;
        margin-bottom: 4px;
    }

    .period-label {
        font-size: 0.73rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 6px 10px;
        border-radius: 8px;
        display: inline-flex;
        align-items: center;
        gap: 5px;
        margin-bottom: 10px;
    }
    .period-morning  { background: rgba(245,158,11,0.12); color: #FCD34D; }
    .period-afternoon{ background: rgba(59,130,246,0.12); color: #93C5FD; }
    .period-evening  { background: rgba(139,92,246,0.12); color: #C4B5FD; }

    .act-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 8px;
        transition: all 0.2s;
    }
    .act-card:hover { background: rgba(255,255,255,0.06); border-color: var(--border-bright); }
    .act-time { font-size: 0.72rem; font-weight: 700; color: var(--accent-cyan); margin-bottom: 4px; }
    .act-desc { font-size: 0.88rem; font-weight: 600; color: var(--text-primary); margin-bottom: 6px; }
    .act-footer { display: flex; justify-content: space-between; align-items: center; }
    .act-loc  { font-size: 0.72rem; color: var(--text-muted); }
    .act-cost { font-size: 0.72rem; font-weight: 700; color: var(--accent-emerald); }
    .act-cost-free { color: var(--text-muted); }

    /* ─────────────────────────────────────────────
       WEATHER CARDS
    ───────────────────────────────────────────── */
    .weather-day-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 14px;
        text-align: center;
        flex: 1;
        min-width: 80px;
    }
    .weather-day-num { font-size: 0.68rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; }
    .weather-cond    { font-size: 0.8rem; font-weight: 600; color: var(--text-primary); margin: 6px 0 4px; }
    .weather-temp    { font-size: 0.75rem; color: var(--accent-amber); font-weight: 600; }
    .weather-suit    { font-size: 0.68rem; color: var(--text-muted); margin-top: 4px; }
    .weather-days-row { display: flex; gap: 8px; margin-bottom: 14px; }

    .warn-box {
        background: rgba(239,68,68,0.10);
        border: 1px solid rgba(239,68,68,0.25);
        border-radius: 10px;
        padding: 12px 14px;
        font-size: 0.82rem;
        color: #FCA5A5;
        display: flex;
        gap: 8px;
        align-items: flex-start;
        margin-bottom: 14px;
    }

    /* ─────────────────────────────────────────────
       BUDGET STATUS
    ───────────────────────────────────────────── */
    .budget-status-ok  { background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.28); border-radius: 10px; padding: 10px 14px; font-size: 0.82rem; color: #6EE7B7; font-weight: 600; margin-bottom: 12px; }
    .budget-status-bad { background: rgba(239,68,68,0.12);  border: 1px solid rgba(239,68,68,0.28);  border-radius: 10px; padding: 10px 14px; font-size: 0.82rem; color: #FCA5A5; font-weight: 600; margin-bottom: 12px; }

    .saving-tip {
        background: rgba(245,158,11,0.08);
        border-left: 3px solid var(--accent-amber);
        border-radius: 0 8px 8px 0;
        padding: 8px 12px;
        font-size: 0.8rem;
        color: #FDE68A;
        margin-bottom: 6px;
    }

    /* ─────────────────────────────────────────────
       LANDING (no data)
    ───────────────────────────────────────────── */
    .agent-showcase {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 14px;
        margin: 28px 0;
    }
    .agent-item {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 20px 18px;
        transition: all 0.25s;
        cursor: default;
    }
    .agent-item:hover {
        background: var(--bg-card-hover);
        border-color: var(--border-bright);
        transform: translateY(-2px);
    }
    .agent-emoji { font-size: 2rem; margin-bottom: 10px; }
    .agent-name { font-size: 0.88rem; font-weight: 700; color: var(--text-primary); margin-bottom: 5px; }
    .agent-desc { font-size: 0.76rem; color: var(--text-secondary); line-height: 1.5; }

    .landing-cta {
        background: linear-gradient(135deg, rgba(59,130,246,0.1), rgba(124,58,237,0.1));
        border: 1px solid rgba(99,102,241,0.25);
        border-radius: 16px;
        padding: 24px 28px;
        text-align: center;
        margin: 24px 0;
    }
    .landing-cta h3 { font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin-bottom: 8px; }
    .landing-cta p  { font-size: 0.88rem; color: var(--text-secondary); margin: 0; }

    /* Streamlit tab overrides */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-card) !important;
        border-radius: 10px !important;
        border: 1px solid var(--border) !important;
        gap: 4px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 7px !important;
        color: var(--text-muted) !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(59,130,246,0.2) !important;
        color: var(--accent-cyan) !important;
    }
</style>
""", unsafe_allow_html=True)


# ─── Helpers ───────────────────────────────────────────────────────────────────
def fmt_vnd(n):
    """Format number as VND string."""
    try:
        return f"{int(n):,} ₫"
    except:
        return str(n)

def weather_emoji(condition: str) -> str:
    c = condition.lower()
    if any(x in c for x in ["nắng", "sunny", "clear"]): return "☀️"
    if any(x in c for x in ["sương", "fog", "mist"]): return "🌫️"
    if any(x in c for x in ["mưa", "rain"]): return "🌧️"
    if any(x in c for x in ["mây", "cloud"]): return "⛅"
    if any(x in c for x in ["dông", "thunder"]): return "⛈️"
    return "🌤️"


# ─── HERO HEADER ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-badge">✦ Powered by Google Gemini &amp; Multi-Agent ADK</div>
    <h1 class="hero-title">AI Multi-Agent<br>Travel Planner</h1>
    <p class="hero-subtitle">
        Hệ thống lập kế hoạch du lịch thông minh với 5 Sub-Agents chuyên biệt được điều phối bởi Host Agent theo giao thức A2A.
    </p>
    <div class="hero-divider"></div>
</div>
""", unsafe_allow_html=True)


# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">✈️</div>
        <div>
            <div class="sidebar-logo-text">Travel Planner AI</div>
            <div class="sidebar-logo-sub">Multi-Agent System • ADK</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">📍 Điểm đi & đến</div>', unsafe_allow_html=True)
    origin      = st.text_input("Điểm xuất phát", value="TP. Hồ Chí Minh", placeholder="VD: Hà Nội")
    destination = st.text_input("Điểm đến",       value="Đà Lạt",          placeholder="VD: Đà Lạt, Hội An, Phú Quốc...")

    st.markdown('<div class="sidebar-section">📅 Thời gian</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Khởi hành", min_value=datetime.today())
    with col2:
        duration_days = st.number_input("Số ngày", min_value=1, max_value=14, value=3)

    st.markdown('<div class="sidebar-section">💰 Ngân sách</div>', unsafe_allow_html=True)
    budget = st.number_input(
        "Ngân sách tối đa (VND)",
        min_value=1_000_000, max_value=100_000_000,
        value=6_000_000, step=500_000,
        format="%d"
    )
    st.caption(f"≈ {budget/1_000_000:.1f} triệu VND")

    st.markdown('<div class="sidebar-section">✨ Sở thích</div>', unsafe_allow_html=True)
    preferences = st.text_area(
        "Yêu cầu / Sở thích",
        value="Thích đi các quán cà phê đẹp ngắm cảnh, thích ẩm thực địa phương, hạn chế các hoạt động trekking tốn sức nhiều.",
        placeholder="VD: đi nghỉ dưỡng, có trẻ nhỏ, muốn trekking, ăn uống bình dân...",
        height=100
    )

    st.markdown("<br>", unsafe_allow_html=True)
    submit_btn = st.button("🚀  Lên Kế Hoạch Ngay", use_container_width=True, type="primary")

    # Tech stack footer in sidebar
    st.markdown("""
    <div style='margin-top:28px; padding-top:18px; border-top:1px solid rgba(255,255,255,0.06);'>
        <div style='font-size:0.68rem; color:#475569; text-align:center; line-height:1.9;'>
            🐍 FastAPI &nbsp;•&nbsp; 🤖 Google ADK<br>
            🔗 A2A Protocol &nbsp;•&nbsp; ☁️ Cloud Run<br>
            📊 Streamlit &nbsp;•&nbsp; 🐳 Docker
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── MAIN LOGIC ────────────────────────────────────────────────────────────────
if submit_btn:
    payload = {
        "origin": origin,
        "destination": destination,
        "start_date": start_date.strftime("%d/%m/%Y"),
        "duration_days": int(duration_days),
        "budget": float(budget),
        "preferences": preferences
    }

    with st.spinner("🧠 Host Agent đang điều phối các Sub-Agents..."):
        try:
            response = httpx.post(f"{BACKEND_URL}/api/plan", json=payload, timeout=120.0)
            if response.status_code == 200:
                st.session_state["plan_data"] = response.json()
                st.success("🎉 Kế hoạch du lịch đã được tạo thành công!")
            else:
                st.error(f"Lỗi hệ thống ({response.status_code}): {response.text}")
        except Exception as e:
            st.error(f"Không thể kết nối đến Backend tại {BACKEND_URL}. Chi tiết: {e}")


# ─── RESULT VIEW ────────────────────────────────────────────────────────────────
if "plan_data" in st.session_state:
    plan      = st.session_state["plan_data"]
    fd        = plan["flight_data"]
    hd        = plan["hotel_data"]
    wd        = plan["weather_data"]
    bd        = plan["budget_data"]
    itinerary = plan["itinerary_data"]
    alloc     = bd["allocation"]
    rec_flight = fd["options"][fd["recommended_option_index"]]
    rec_hotel  = hd["recommendations"][hd["recommended_index"]]

    # ── Agent Pipeline Tracker ──────────────────────────────────────────────────
    st.markdown("""
    <div style='display:flex;align-items:center;gap:10px;margin-bottom:6px;'>
        <div style='font-size:0.72rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#475569;'>Agent Pipeline</div>
        <div style='flex:1;height:1px;background:rgba(255,255,255,0.06);'></div>
    </div>
    <div class="pipeline-wrap">
        <div class="pipeline-node">
            <div class="pipeline-icon done">🎯</div>
            <div class="pipeline-label">Host<br>Agent</div>
        </div>
        <div class="pipeline-connector"></div>
        <div class="pipeline-node">
            <div class="pipeline-icon done">✈️</div>
            <div class="pipeline-label">Flight<br>Agent</div>
        </div>
        <div class="pipeline-connector"></div>
        <div class="pipeline-node">
            <div class="pipeline-icon done">🌤️</div>
            <div class="pipeline-label">Weather<br>Agent</div>
        </div>
        <div class="pipeline-connector"></div>
        <div class="pipeline-node">
            <div class="pipeline-icon done">🏨</div>
            <div class="pipeline-label">Hotel<br>Agent</div>
        </div>
        <div class="pipeline-connector"></div>
        <div class="pipeline-node">
            <div class="pipeline-icon done">🗓️</div>
            <div class="pipeline-label">Itinerary<br>Agent</div>
        </div>
        <div class="pipeline-connector"></div>
        <div class="pipeline-node">
            <div class="pipeline-icon done">💰</div>
            <div class="pipeline-label">Budget<br>Agent</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Row ─────────────────────────────────────────────────────────────────
    savings = plan["budget_limit"] - bd["total_cost"]
    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi-chip">
            <div class="kpi-label">🏁 Điểm đến</div>
            <div class="kpi-value">{plan['destination']}</div>
            <div class="kpi-sub">{plan['duration_days']} ngày • {start_date.strftime('%d/%m/%Y')}</div>
        </div>
        <div class="kpi-chip">
            <div class="kpi-label">💸 Chi phí ước tính</div>
            <div class="kpi-value" style="color:var(--accent-emerald);">{fmt_vnd(bd['total_cost'])}</div>
            <div class="kpi-sub">Ngân sách: {fmt_vnd(plan['budget_limit'])}</div>
        </div>
        <div class="kpi-chip">
            <div class="kpi-label">💚 Dư ngân sách</div>
            <div class="kpi-value" style="color:{'var(--accent-emerald)' if savings >= 0 else 'var(--accent-red)'};">{fmt_vnd(abs(savings))}</div>
            <div class="kpi-sub">{'Còn dư' if savings >= 0 else 'Vượt quá'}</div>
        </div>
        <div class="kpi-chip">
            <div class="kpi-label">🚄 Phương tiện</div>
            <div class="kpi-value" style="font-size:1.1rem;">{rec_flight['carrier']}</div>
            <div class="kpi-sub">{rec_flight['departure_time']} → {rec_flight['arrival_time']}</div>
        </div>
        <div class="kpi-chip">
            <div class="kpi-label">🏨 Lưu trú</div>
            <div class="kpi-value" style="font-size:0.95rem;">{rec_hotel['name'][:22]}{'…' if len(rec_hotel['name'])>22 else ''}</div>
            <div class="kpi-sub">{rec_hotel['type']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ────────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["🗓️  Lịch Trình", "🚄🏨  Di Chuyển & Lưu Trú", "💰  Ngân Sách", "🛠️  Agent Logs"])

    # ── TAB 1: Itinerary ────────────────────────────────────────────────────────
    with tab1:
        if not itinerary["daily_plans"]:
            st.warning("Không có lịch trình được sinh ra. Vui lòng thử lại.")
        else:
            for day in itinerary["daily_plans"]:
                # Day header
                st.markdown(f"""
                <div class="day-header">
                    <div class="day-badge">Ngày {day['day']}</div>
                    <div>
                        <div class="day-title">{day['title']}</div>
                        <div class="day-route">🛣️ {day['route_optimization']}</div>
                    </div>
                </div>
                <div class="day-body">
                """, unsafe_allow_html=True)

                m_col, a_col, e_col = st.columns(3)

                def render_activities(container, acts, period_class, period_label, period_emoji):
                    with container:
                        st.markdown(f'<div class="period-label {period_class}">{period_emoji} {period_label}</div>', unsafe_allow_html=True)
                        if not acts:
                            st.markdown('<div style="color:var(--text-muted);font-size:0.8rem;padding:8px 0;">—</div>', unsafe_allow_html=True)
                        for act in acts:
                            cost_str = fmt_vnd(act['estimated_cost']) if act['estimated_cost'] > 0 else "Miễn phí"
                            cost_class = "act-cost" if act['estimated_cost'] > 0 else "act-cost act-cost-free"
                            st.markdown(f"""
                            <div class="act-card">
                                <div class="act-time">{act['time_slot']}</div>
                                <div class="act-desc">{act['description']}</div>
                                <div class="act-footer">
                                    <span class="act-loc">📍 {act['location']}</span>
                                    <span class="{cost_class}">{cost_str}</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                render_activities(m_col, day["morning"],   "period-morning",   "Buổi Sáng", "☀️")
                render_activities(a_col, day["afternoon"], "period-afternoon", "Buổi Chiều", "🌤️")
                render_activities(e_col, day["evening"],   "period-evening",   "Buổi Tối",  "🌙")

                st.markdown("</div>", unsafe_allow_html=True)

    # ── TAB 2: Flight & Hotel ───────────────────────────────────────────────────
    with tab2:
        fl_col, ht_col = st.columns(2, gap="large")

        with fl_col:
            # Recommended highlight
            amenities_html = "".join([f'<span class="tag-pill">{a}</span>' for a in rec_flight.get("pros_cons", "").split(";")])
            st.markdown(f"""
            <div class="info-card">
                <div class="info-card-header">
                    <div class="info-card-icon" style="background:rgba(59,130,246,0.15);">✈️</div>
                    <div>
                        <div class="info-card-title">Phương Tiện Di Chuyển</div>
                        <div class="info-card-sub">{fd['transport_type']} • Được đề xuất</div>
                    </div>
                </div>
                <div class="info-row"><span class="info-label">Hãng / Nhà xe</span><span class="info-val">{rec_flight['carrier']}</span></div>
                <div class="info-row"><span class="info-label">Thời gian di chuyển</span><span class="info-val">{rec_flight['duration']}</span></div>
                <div class="info-row"><span class="info-label">Khởi hành</span><span class="info-val">{rec_flight['departure_time']}</span></div>
                <div class="info-row"><span class="info-label">Đến nơi</span><span class="info-val">{rec_flight['arrival_time']}</span></div>
                <div style="height:1px;background:var(--border);margin:12px 0;"></div>
                <div class="info-row"><span class="info-label">Giá vé ước tính</span><span class="price-tag">{fmt_vnd(rec_flight['price_estimate'])}</span></div>
                <div style="margin-top:10px;font-size:0.76rem;color:var(--text-secondary);font-style:italic;">{rec_flight['pros_cons']}</div>
            </div>
            """, unsafe_allow_html=True)

            # Other options
            if len(fd["options"]) > 1:
                with st.expander(f"🔄 Xem thêm {len(fd['options'])-1} phương án khác"):
                    for i, opt in enumerate(fd["options"]):
                        if i == fd["recommended_option_index"]: continue
                        st.markdown(f"""
                        <div class="glass-card" style="padding:14px 16px;">
                            <div style="font-weight:600;font-size:0.88rem;">{opt['carrier']}</div>
                            <div style="font-size:0.78rem;color:var(--text-secondary);margin-top:4px;">
                                {opt['departure_time']} → {opt['arrival_time']} &nbsp;|&nbsp; {opt['duration']} &nbsp;|&nbsp;
                                <span style="color:var(--accent-emerald);font-weight:700;">{fmt_vnd(opt['price_estimate'])}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

        with ht_col:
            amenities_tags = "".join([f'<span class="tag-pill">{a}</span>' for a in rec_hotel.get("amenities", [])])
            st.markdown(f"""
            <div class="info-card">
                <div class="info-card-header">
                    <div class="info-card-icon" style="background:rgba(236,72,153,0.15);">🏨</div>
                    <div>
                        <div class="info-card-title">Nơi Lưu Trú</div>
                        <div class="info-card-sub">{rec_hotel['type']} • Được đề xuất</div>
                    </div>
                </div>
                <div class="info-row"><span class="info-label">Tên khách sạn</span><span class="info-val">{rec_hotel['name']}</span></div>
                <div class="info-row"><span class="info-label">Địa chỉ</span><span class="info-val">{rec_hotel['address']}</span></div>
                <div class="info-row"><span class="info-label">Giá / đêm</span><span class="info-val">{fmt_vnd(rec_hotel['price_per_night'])}</span></div>
                <div class="info-row"><span class="info-label">Tổng lưu trú ({plan['duration_days']-1} đêm)</span><span class="price-tag">{fmt_vnd(rec_hotel['total_price'])}</span></div>
                <div style="height:1px;background:var(--border);margin:12px 0;"></div>
                <div style="font-size:0.78rem;color:var(--text-secondary);margin-bottom:8px;font-weight:600;">TIỆN ÍCH</div>
                <div>{amenities_tags}</div>
                <div style="margin-top:12px;font-size:0.76rem;color:var(--text-secondary);font-style:italic;">{rec_hotel['why_recommended']}</div>
            </div>
            """, unsafe_allow_html=True)

            if len(hd["recommendations"]) > 1:
                with st.expander(f"🔄 Xem thêm {len(hd['recommendations'])-1} lựa chọn khác"):
                    for i, hotel in enumerate(hd["recommendations"]):
                        if i == hd["recommended_index"]: continue
                        tags = "".join([f'<span class="tag-pill">{a}</span>' for a in hotel.get("amenities", [])[:3]])
                        st.markdown(f"""
                        <div class="glass-card" style="padding:14px 16px;">
                            <div style="font-weight:600;font-size:0.88rem;">{hotel['name']}</div>
                            <div style="font-size:0.76rem;color:var(--text-secondary);margin:4px 0;">{hotel['address']}</div>
                            <div style="font-size:0.78rem;">
                                <span style="color:var(--accent-emerald);font-weight:700;">{fmt_vnd(hotel['price_per_night'])}/đêm</span>
                                &nbsp;·&nbsp; Tổng: <b>{fmt_vnd(hotel['total_price'])}</b>
                            </div>
                            <div style="margin-top:6px;">{tags}</div>
                        </div>
                        """, unsafe_allow_html=True)

        # Weather section inside tab 2
        st.markdown("---")
        st.markdown("#### ☀️ Thời Tiết Dự Báo")
        wc1, wc2 = st.columns([3, 2])

        with wc1:
            if wd.get("general_warnings"):
                st.markdown(f"""
                <div class="warn-box">⚠️ <span>{wd['general_warnings']}</span></div>
                """, unsafe_allow_html=True)

            days_html = '<div class="weather-days-row">'
            for fc in wd["forecast"]:
                days_html += f"""
                <div class="weather-day-card">
                    <div class="weather-day-num">Ngày {fc['day']}</div>
                    <div style="font-size:1.5rem;">{weather_emoji(fc['condition'])}</div>
                    <div class="weather-cond">{fc['condition']}</div>
                    <div class="weather-temp">{fc['temp_range']}</div>
                    <div class="weather-suit">{fc['activity_suitability']}</div>
                </div>"""
            days_html += "</div>"
            st.markdown(days_html, unsafe_allow_html=True)

        with wc2:
            st.markdown("""<div style='font-size:0.8rem;font-weight:700;color:var(--text-secondary);margin-bottom:10px;'>🧳 GỢI Ý HÀNH LÝ</div>""", unsafe_allow_html=True)
            for tip in wd.get("luggage_tips", []):
                st.markdown(f"""
                <div style='display:flex;gap:8px;align-items:flex-start;padding:6px 0;border-bottom:1px solid var(--border);'>
                    <span style='color:var(--accent-cyan);'>→</span>
                    <span style='font-size:0.82rem;color:var(--text-secondary);'>{tip}</span>
                </div>
                """, unsafe_allow_html=True)

    # ── TAB 3: Budget ───────────────────────────────────────────────────────────
    with tab3:
        b1, b2 = st.columns([1, 1], gap="large")

        with b1:
            # Status
            status_class = "budget-status-ok" if bd["is_feasible"] else "budget-status-bad"
            status_icon  = "✅" if bd["is_feasible"] else "❌"
            st.markdown(f"""
            <div class="{status_class}">{status_icon} &nbsp;{bd['status']} — Chi phí dự kiến: <strong>{fmt_vnd(bd['total_cost'])}</strong> / Hạn mức: {fmt_vnd(plan['budget_limit'])}</div>
            """, unsafe_allow_html=True)

            # Donut chart with Plotly
            labels  = ["Di Chuyển", "Lưu Trú", "Hoạt Động", "Ăn Uống", "Dự Phòng"]
            values  = [
                alloc["transportation"],
                alloc["accommodation"],
                alloc["activities"],
                alloc["food_and_beverage"],
                alloc["contingency"]
            ]
            colors = ["#3B82F6", "#EC4899", "#8B5CF6", "#F59E0B", "#6B7280"]

            fig = go.Figure(go.Pie(
                labels=labels, values=values,
                hole=0.62,
                marker=dict(colors=colors, line=dict(color="#070B14", width=3)),
                textinfo="percent",
                textfont=dict(size=11, family="Plus Jakarta Sans"),
                hovertemplate="<b>%{label}</b><br>%{value:,} ₫<br>%{percent}<extra></extra>"
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94A3B8", family="Plus Jakarta Sans"),
                legend=dict(
                    orientation="v", x=1.02, y=0.5,
                    font=dict(size=11),
                    bgcolor="rgba(0,0,0,0)"
                ),
                margin=dict(l=0, r=80, t=20, b=20),
                annotations=[dict(
                    text=f"<b>{fmt_vnd(bd['total_cost'])}</b>",
                    x=0.5, y=0.5, font_size=13,
                    font=dict(color="#F0F4FF", family="Plus Jakarta Sans"),
                    showarrow=False
                )]
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with b2:
            st.markdown("##### 📊 Chi Tiết Phân Bổ")
            budget_items = [
                ("✈️ Di Chuyển",   alloc["transportation"],  "#3B82F6"),
                ("🏨 Lưu Trú",     alloc["accommodation"],   "#EC4899"),
                ("🎭 Hoạt Động",   alloc["activities"],      "#8B5CF6"),
                ("🍜 Ăn Uống",     alloc["food_and_beverage"],"#F59E0B"),
                ("🛡️ Dự Phòng",    alloc["contingency"],     "#6B7280"),
            ]
            total = bd["total_cost"] or 1
            for icon_label, amount, color in budget_items:
                pct = amount / plan["budget_limit"] * 100 if plan["budget_limit"] else 0
                bar_w = min(amount / total * 100, 100)
                st.markdown(f"""
                <div style="margin-bottom:14px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                        <span style="font-size:0.82rem;font-weight:600;color:var(--text-primary);">{icon_label}</span>
                        <span style="font-size:0.82rem;font-weight:700;color:{color};">{fmt_vnd(amount)}</span>
                    </div>
                    <div style="background:rgba(255,255,255,0.06);border-radius:99px;height:6px;overflow:hidden;">
                        <div style="width:{bar_w:.1f}%;background:{color};height:100%;border-radius:99px;transition:width 0.6s ease;"></div>
                    </div>
                    <div style="font-size:0.68rem;color:var(--text-muted);margin-top:3px;">{pct:.1f}% ngân sách</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("##### 💡 Mẹo Tiết Kiệm")
            for tip in bd.get("saving_tips", []):
                st.markdown(f'<div class="saving-tip">💡 {tip}</div>', unsafe_allow_html=True)

    # ── TAB 4: Agent Logs ───────────────────────────────────────────────────────
    with tab4:
        st.markdown("""
        <p style='font-size:0.85rem;color:var(--text-secondary);margin-bottom:16px;'>
        Nhật ký thời gian thực thể hiện quá trình Host Agent điều phối các Sub-Agent theo giao thức <strong style='color:var(--accent-cyan);'>Agent-to-Agent (A2A)</strong>.
        </p>
        """, unsafe_allow_html=True)

        log_body = ""
        for i, log in enumerate(plan["logs"]):
            step = log["step"]
            msg  = log["message"]
            is_ok  = "thành công" in msg.lower() or "hoàn thành" in msg.lower() or "khuyên dùng" in msg.lower()
            is_err = "thất bại" in msg.lower() or "lỗi" in msg.lower()
            tag_class = "log-tag-ok" if is_ok else ("log-tag-err" if is_err else "log-tag-host")
            time_str  = f"[{i:02d}]"
            log_body += f"""<div class="log-line">
                <span class="log-time">{time_str}</span>
                &nbsp;<span class="{tag_class}">[{step}]</span>
                &nbsp;<span class="log-msg">{msg}</span>
            </div>"""

        st.markdown(f"""
        <div class="terminal-wrap">
            <div class="terminal-bar">
                <div class="terminal-dot" style="background:#EF4444;"></div>
                <div class="terminal-dot" style="background:#F59E0B;"></div>
                <div class="terminal-dot" style="background:#10B981;"></div>
                <span style="font-size:0.72rem;color:var(--text-muted);margin-left:8px;">host_agent.log — A2A Simulation</span>
            </div>
            <div class="terminal-body">{log_body}</div>
        </div>
        """, unsafe_allow_html=True)

        # Agent Architecture Visual
        st.markdown("##### 🔗 Sơ Đồ Kiến Trúc Agent")
        st.markdown("""
        <div style='background:rgba(255,255,255,0.02);border:1px solid var(--border);border-radius:14px;padding:24px;'>
            <div style='display:grid;grid-template-columns:1fr auto 1fr auto 1fr auto 1fr auto 1fr;align-items:center;gap:6px;text-align:center;'>
                <div style='background:linear-gradient(135deg,#3B82F6,#7C3AED);border-radius:12px;padding:12px 8px;'>
                    <div style='font-size:1.3rem;'>🎯</div>
                    <div style='font-size:0.72rem;font-weight:700;margin-top:4px;'>Host Agent</div>
                    <div style='font-size:0.62rem;color:rgba(255,255,255,0.6);'>Orchestrator</div>
                </div>
                <div style='color:var(--accent-cyan);font-size:1.2rem;'>⇄</div>
                <div style='background:rgba(59,130,246,0.12);border:1px solid rgba(59,130,246,0.25);border-radius:10px;padding:10px 8px;'>
                    <div style='font-size:1.1rem;'>✈️</div>
                    <div style='font-size:0.68rem;font-weight:600;margin-top:3px;'>Flight</div>
                </div>
                <div style='color:var(--accent-cyan);font-size:1.2rem;'>⇄</div>
                <div style='background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.25);border-radius:10px;padding:10px 8px;'>
                    <div style='font-size:1.1rem;'>🌤️</div>
                    <div style='font-size:0.68rem;font-weight:600;margin-top:3px;'>Weather</div>
                </div>
                <div style='color:var(--accent-cyan);font-size:1.2rem;'>⇄</div>
                <div style='background:rgba(236,72,153,0.12);border:1px solid rgba(236,72,153,0.25);border-radius:10px;padding:10px 8px;'>
                    <div style='font-size:1.1rem;'>🏨</div>
                    <div style='font-size:0.68rem;font-weight:600;margin-top:3px;'>Hotel</div>
                </div>
                <div style='color:var(--accent-cyan);font-size:1.2rem;'>⇄</div>
                <div style='background:rgba(139,92,246,0.12);border:1px solid rgba(139,92,246,0.25);border-radius:10px;padding:10px 8px;'>
                    <div style='font-size:1.1rem;'>🗓️</div>
                    <div style='font-size:0.68rem;font-weight:600;margin-top:3px;'>Itinerary</div>
                </div>
            </div>
            <div style='text-align:center;margin-top:14px;font-size:0.72rem;color:var(--text-muted);'>
                Tất cả Sub-Agents giao tiếp với Host Agent thông qua giao thức <strong style='color:var(--accent-cyan);'>A2A (Agent-to-Agent)</strong>
                và sử dụng <strong style='color:var(--accent-violet);'>Google Gemini API</strong> để sinh nội dung có cấu trúc.
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─── LANDING STATE (No data) ───────────────────────────────────────────────────
else:
    st.markdown("""
    <div class="landing-cta">
        <h3>👈 Nhập thông tin chuyến đi và nhấn <em>"Lên Kế Hoạch Ngay"</em></h3>
        <p>Host Agent sẽ tự động điều phối 5 Sub-Agents để tạo ra kế hoạch du lịch tối ưu cho bạn trong vài giây.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 🤖 Các Sub-Agent trong Hệ Thống")
    st.markdown("""
    <div class="agent-showcase">
        <div class="agent-item">
            <div class="agent-emoji">✈️</div>
            <div class="agent-name">Flight Agent</div>
            <div class="agent-desc">Gợi ý phương tiện di chuyển, ước lượng thời gian và chi phí vé.</div>
        </div>
        <div class="agent-item">
            <div class="agent-emoji">🌤️</div>
            <div class="agent-name">Weather Agent</div>
            <div class="agent-desc">Dự báo thời tiết từng ngày, gợi ý trang phục và hành lý phù hợp.</div>
        </div>
        <div class="agent-item">
            <div class="agent-emoji">🏨</div>
            <div class="agent-name">Hotel Agent</div>
            <div class="agent-desc">Đề xuất khách sạn, homestay phù hợp vị trí và ngân sách.</div>
        </div>
        <div class="agent-item">
            <div class="agent-emoji">🗓️</div>
            <div class="agent-name">Itinerary Agent</div>
            <div class="agent-desc">Lập lịch trình chi tiết từng ngày, tối ưu hóa tuyến đường di chuyển.</div>
        </div>
        <div class="agent-item">
            <div class="agent-emoji">💰</div>
            <div class="agent-name">Budget Agent</div>
            <div class="agent-desc">Phân bổ ngân sách, kiểm tra tính khả thi và gợi ý tiết kiệm chi phí.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Architecture diagram on landing
    st.markdown("#### 🔗 Luồng Xử Lý A2A")
    cols = st.columns(5)
    steps = [
        ("📝", "Nhập yêu cầu", "Người dùng điền form"),
        ("🎯", "Host Agent phân tích", "Phân rã thành subtasks"),
        ("🤖", "Sub-Agents xử lý", "5 Agents hoạt động song song"),
        ("🔗", "Tổng hợp A2A", "Host Agent kết hợp kết quả"),
        ("📊", "Hiển thị kết quả", "Lịch trình hoàn chỉnh"),
    ]
    for col, (emoji, title, desc) in zip(cols, steps):
        with col:
            st.markdown(f"""
            <div style='text-align:center;padding:16px 8px;'>
                <div style='font-size:2rem;margin-bottom:8px;'>{emoji}</div>
                <div style='font-size:0.8rem;font-weight:700;color:var(--text-primary);margin-bottom:4px;'>{title}</div>
                <div style='font-size:0.72rem;color:var(--text-muted);line-height:1.4;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)
