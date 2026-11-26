import math
import streamlit as st
import pandas as pd
import joblib
import altair as alt

st.set_page_config(
    page_title="Mobile Price Predictor",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Custom Theme: Animated Microchip / PCB Video Background + Frosted Silicon UI
# ---------------------------------------------------------------------------
FEATURE_META = {
    "ram": ("RAM", "MB"),
    "int_memory": ("Internal Storage", "GB"),
    "battery_power": ("Battery Capacity", "mAh"),
    "px_width": ("Resolution Width", "px"),
    "px_height": ("Resolution Height", "px"),
    "sc_w": ("Screen Width", "cm"),
    "sc_h": ("Screen Height", "cm"),
    "pc": ("Primary Camera", "MP"),
    "mobile_wt": ("Weight", "g"),
    "touch_screen": ("Touch Screen", "0 = No, 1 = Yes"),
}

UNIT_INPUT_CSS = "\n".join(
    f"""
    div[data-testid="stNumberInput"]:has(input[aria-label="{label}"]) div[data-baseweb="base-input"]::after {{
        content: "{unit}";
        display: flex;
        align-items: center;
        padding-right: 0.55rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.76rem;
        font-weight: 500;
        color: #94a3b8;
        pointer-events: none;
        user-select: none;
    }}
    """
    for feat, (label, unit) in FEATURE_META.items()
    if unit and feat != "touch_screen"
)

st.markdown(
    f"""
    <video autoplay loop muted playsinline id="pcb-bg-video">
        <source src="app/static/pcb_bg.mp4" type="video/mp4">
    </video>
    <div id="pcb-bg-overlay"></div>

    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {{
        --bg-base: #041624;
        --bg-card: rgba(4, 15, 26, 0.93);
        --bg-surface: rgba(6, 22, 36, 0.94);
        --bg-surface-2: rgba(10, 34, 54, 0.94);
        --border-line: rgba(56, 189, 248, 0.30);
        --text-main: #f1f5f9;
        --text-sub: #cbd5e1;
        --text-muted: #94a3b8;
        --accent: #38bdf8;
        --brand: #0284c7;
        --brand-hover: #0ea5e9;
    }}

    /* Full-bleed looping PCB circuit video background */
    #pcb-bg-video {{
        position: fixed;
        inset: 0;
        width: 100vw;
        height: 100vh;
        object-fit: cover;
        z-index: 0;
        pointer-events: none;
        filter: saturate(1.04) brightness(0.76);
    }}

    #pcb-bg-overlay {{
        position: fixed;
        inset: 0;
        z-index: 0;
        pointer-events: none;
        background:
            radial-gradient(circle at 50% 45%, rgba(3, 14, 24, 0.56) 0%, rgba(2, 10, 18, 0.84) 100%);
    }}

    /* Keep Streamlit root containers transparent so the video shows through */
    .stApp,
    div[data-testid="stAppViewContainer"],
    div[data-testid="stMain"],
    section.main {{
        background: transparent !important;
        color: var(--text-main);
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    div[data-testid="stAppViewContainer"] > .main {{
        position: relative;
        z-index: 1;
    }}

    /* Hide Streamlit default menu, footer, toolbar & Deploy button */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stDeployButton,
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"] {{
        display: none !important;
    }}
    header[data-testid="stHeader"] {{
        background: transparent !important;
        height: 0;
        min-height: 0;
    }}

    .block-container {{
        position: relative;
        z-index: 1;
        padding-top: 1.25rem;
        padding-bottom: 2.5rem;
        max-width: 1180px;
    }}

    /* Compact Header Bar - Frosted Silicon Chip Surface */
    .page-header {{
        background: var(--bg-card);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid var(--border-line);
        border-radius: 14px;
        padding: 0.9rem 1.35rem;
        margin-bottom: 1.1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        box-shadow: 0 12px 32px rgba(2, 10, 18, 0.65), 0 0 22px rgba(56, 189, 248, 0.10);
    }}

    .header-left {{
        display: flex;
        align-items: center;
        gap: 0.85rem;
    }}

    .phone-mark {{
        width: 38px;
        height: 38px;
        border-radius: 10px;
        background: var(--bg-surface-2);
        border: 1px solid rgba(56, 189, 248, 0.36);
        box-shadow: inset 0 0 12px rgba(56, 189, 248, 0.14);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }}

    .page-title {{
        font-size: 1.25rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0 0 0.1rem 0;
        letter-spacing: -0.02em;
        line-height: 1.25;
    }}

    .page-subtitle {{
        font-size: 0.86rem;
        color: var(--text-sub);
        margin: 0;
    }}

    .header-meta {{
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 0.78rem;
        font-weight: 500;
        color: #bae6fd;
        background: rgba(14, 165, 233, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.32);
        padding: 0.38rem 0.75rem;
        border-radius: 8px;
        white-space: nowrap;
    }}

    /* Input & Telemetry Cards - Dark frosted silicon over live PCB video */
    div[data-testid="stVerticalBlockBorderWrapper"],
    .st-key-form_card,
    .st-key-card_radar,
    .st-key-card_market,
    .st-key-card_drivers,
    .st-key-card_ram {{
        background: var(--bg-card) !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--border-line) !important;
        border-radius: 14px !important;
        padding: 1.25rem 1.4rem !important;
        box-shadow: 0 16px 40px rgba(1, 8, 16, 0.82), 0 0 22px rgba(56, 189, 248, 0.10) !important;
    }}

    .group-title {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 0.84rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #e2e8f0;
        margin: 1.5rem 0 0.75rem 0;
        padding-bottom: 0.45rem;
        border-bottom: 1px solid rgba(56, 189, 248, 0.22);
    }}

    .group-title::before {{
        content: "";
        width: 7px;
        height: 7px;
        border-radius: 2px;
        background: var(--accent);
        box-shadow: 0 0 8px rgba(56, 189, 248, 0.75);
        flex-shrink: 0;
    }}

    .group-title:first-child {{
        margin-top: 0;
    }}

    /* Labels: sans-serif, crisp contrast */
    div[data-testid="stNumberInput"] label p,
    div[data-testid="stCheckbox"] label p,
    div[data-testid="stToggle"] label p {{
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-size: 0.86rem !important;
        font-weight: 500 !important;
        color: #e2e8f0 !important;
    }}

    /* Number Input: prominent value, subtle steppers, unit suffix */
    div[data-testid="stNumberInput"] div[data-baseweb="input"] {{
        background-color: rgba(4, 18, 30, 0.92) !important;
        border: 1px solid rgba(56, 189, 248, 0.28) !important;
        border-radius: 8px !important;
    }}

    div[data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within {{
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.24) !important;
    }}

    div[data-testid="stNumberInput"] div[data-baseweb="base-input"] {{
        background-color: transparent !important;
    }}

    div[data-testid="stNumberInput"] input {{
        background-color: transparent !important;
        color: #f8fafc !important;
        border: none !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.96rem !important;
        font-weight: 500 !important;
    }}

    div[data-testid="stNumberInput"] button {{
        background-color: transparent !important;
        border: none !important;
        color: #64748b !important;
        transition: color 0.15s ease, background-color 0.15s ease;
    }}

    div[data-testid="stNumberInput"] button:hover {{
        background-color: rgba(56, 189, 248, 0.14) !important;
        color: var(--accent) !important;
    }}

    {UNIT_INPUT_CSS}

    /* Primary Predict Button */
    div.stButton > button {{
        width: 100%;
        margin-top: 1.1rem;
        padding: 0.72rem 1.2rem;
        border-radius: 10px;
        border: 1px solid rgba(125, 211, 252, 0.45);
        background: linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%);
        color: #ffffff;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.96rem;
        font-weight: 600;
        box-shadow: 0 6px 20px rgba(14, 165, 233, 0.30);
        transition: filter 0.15s ease, transform 0.12s ease, box-shadow 0.15s ease;
    }}

    div.stButton > button:hover {{
        filter: brightness(1.08);
        color: #ffffff;
        box-shadow: 0 8px 24px rgba(56, 189, 248, 0.42);
        transform: translateY(-1px);
    }}

    /* Sticky Preview Column on Desktop */
    @media (min-width: 769px) {{
        div[data-testid="stHorizontalBlock"] {{
            align-items: flex-start;
        }}
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2),
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) {{
            position: sticky;
            top: 1.25rem;
            align-self: flex-start;
        }}
    }}

    /* Realistic Smartphone Mockup Preview */
    .phone-chassis {{
        background: linear-gradient(165deg, rgba(10, 36, 56, 0.94) 0%, rgba(5, 20, 34, 0.96) 100%);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 2px solid rgba(56, 189, 248, 0.36);
        border-radius: 34px;
        padding: 13px;
        box-shadow: 0 20px 44px rgba(2, 10, 18, 0.72), 0 0 28px rgba(56, 189, 248, 0.14);
        max-width: 390px;
        margin: 0 auto;
    }}

    .phone-screen {{
        background: rgba(4, 18, 30, 0.94);
        border: 1px solid rgba(56, 189, 248, 0.22);
        border-radius: 24px;
        padding: 0.95rem 1.05rem 1.1rem 1.05rem;
    }}

    .phone-status-bar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 0.72rem;
        font-weight: 500;
        color: var(--text-sub);
        margin-bottom: 0.8rem;
    }}

    .dynamic-island {{
        width: 74px;
        height: 15px;
        background: #04080e;
        border-radius: 999px;
        border: 1px solid #1e293b;
    }}

    .price-readout {{
        background: var(--bg-surface);
        border: 1px solid var(--border-line);
        border-radius: 14px;
        padding: 0.95rem 1rem;
        text-align: center;
        margin-bottom: 0.85rem;
    }}

    .price-readout-empty {{
        background: rgba(8, 28, 44, 0.75);
        border: 1px dashed rgba(56, 189, 248, 0.30);
    }}

    .price-label {{
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #cbd5e1;
        margin-bottom: 0.25rem;
    }}

    .price-value {{
        font-size: 1.45rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
    }}

    .mono-num {{
        font-family: 'JetBrains Mono', monospace;
    }}

    .tier-steps {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 5px;
        margin-top: 0.7rem;
    }}

    .tier-step {{
        height: 5px;
        border-radius: 999px;
        background: #1e293b;
    }}

    .spec-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.83rem;
    }}

    .spec-table tr {{
        border-bottom: 1px solid rgba(56, 189, 248, 0.12);
    }}

    .spec-table tr:last-child {{
        border-bottom: none;
    }}

    .spec-table td {{
        padding: 0.44rem 0.2rem;
    }}

    .spec-key {{
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #cbd5e1;
    }}

    .spec-val {{
        text-align: right;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500;
        color: #f8fafc;
    }}

    .confidence-box {{
        background: var(--bg-card);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid var(--border-line);
        border-radius: 16px;
        padding: 1rem 1.15rem;
        max-width: 390px;
        margin: 0.85rem auto 0 auto;
        box-shadow: 0 14px 36px rgba(2, 10, 18, 0.70), 0 0 22px rgba(56, 189, 248, 0.08);
    }}

    div[data-testid="stAlert"] {{
        background: rgba(6, 24, 40, 0.90) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 12px !important;
    }}

    /* Telemetry & Analytics Section */
    .analytics-banner {{
        background: var(--bg-card);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid var(--border-line);
        border-radius: 14px;
        padding: 0.85rem 1.35rem;
        margin: 1.5rem 0 1rem 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        box-shadow: 0 10px 28px rgba(2, 10, 18, 0.60), 0 0 18px rgba(56, 189, 248, 0.08);
    }}

    .analytics-title-wrap {{
        display: flex;
        align-items: center;
        gap: 0.65rem;
    }}

    .telemetry-dot {{
        width: 9px;
        height: 9px;
        border-radius: 999px;
        background: #38bdf8;
        box-shadow: 0 0 10px #38bdf8, 0 0 18px rgba(56, 189, 248, 0.7);
        flex-shrink: 0;
    }}

    .analytics-title {{
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 1.02rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 0;
        letter-spacing: -0.01em;
    }}

    .analytics-sub {{
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 0.82rem;
        color: var(--text-sub);
        margin: 0;
    }}

    .chart-head {{
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        gap: 0.5rem;
        padding-bottom: 0.45rem;
        margin-bottom: 0.65rem;
        border-bottom: 1px solid rgba(56, 189, 248, 0.22);
    }}

    .chart-title {{
        display: flex;
        align-items: center;
        gap: 0.45rem;
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 0.84rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #e2e8f0;
    }}

    .chart-title::before {{
        content: "";
        width: 6px;
        height: 6px;
        border-radius: 2px;
        background: var(--accent);
        box-shadow: 0 0 8px rgba(56, 189, 248, 0.75);
    }}

    .chart-sub {{
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 0.78rem;
        color: #94a3b8;
        margin-bottom: 0.5rem;
    }}

    .radar-wrap {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding-top: 0.15rem;
    }}

    .radar-legend {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1.25rem;
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 0.78rem;
        color: #cbd5e1;
        margin-top: 0.35rem;
    }}

    .radar-legend-item {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
    }}

    .confidence-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 0.84rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #e2e8f0;
        padding-bottom: 0.45rem;
        margin-bottom: 0.75rem;
        border-bottom: 1px solid var(--border-line);
    }}

    .info-tip {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 18px;
        height: 18px;
        border-radius: 999px;
        border: 1px solid rgba(148, 163, 184, 0.45);
        color: #cbd5e1;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: none;
        letter-spacing: 0;
        cursor: help;
    }}

    .prob-row {{
        margin-bottom: 0.55rem;
    }}

    .prob-row:last-child {{
        margin-bottom: 0;
    }}

    .prob-meta {{
        display: flex;
        justify-content: space-between;
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 0.83rem;
        color: #e2e8f0;
        margin-bottom: 0.22rem;
    }}

    .prob-pct {{
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500;
    }}

    .prob-bar-bg {{
        width: 100%;
        height: 7px;
        border-radius: 999px;
        background: #1e293b;
        overflow: hidden;
    }}

    .prob-bar-fill {{
        height: 100%;
        border-radius: 999px;
    }}

    .hw-tiles {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.55rem;
        margin-bottom: 0.75rem;
    }}

    .hw-tile {{
        background: rgba(14, 46, 70, 0.72);
        border: 1px solid rgba(56, 189, 248, 0.20);
        border-radius: 10px;
        padding: 0.55rem 0.7rem;
    }}

    .hw-tile-label {{
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #cbd5e1;
        margin-bottom: 0.15rem;
    }}

    .hw-tile-val {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.94rem;
        font-weight: 600;
        color: #f8fafc;
    }}

    .batt-pill {{
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
    }}

    .batt-icon {{
        width: 24px;
        height: 11px;
        border: 1px solid #64748b;
        border-radius: 2.5px;
        padding: 1.5px;
        display: inline-flex;
        align-items: center;
    }}

    .batt-fill {{
        height: 100%;
        background: #10b981;
        border-radius: 1px;
    }}

    @media (max-width: 768px) {{
        .page-header {{
            flex-direction: column;
            align-items: flex-start;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Load Model & Dataset (Exact same model, features, and scaler)
# ---------------------------------------------------------------------------
model_bundle = joblib.load("mobile_price_model.pkl")

model = model_bundle["model"]
selected_features = model_bundle["selected_features"]
scaler = model_bundle["scaler"]

df = pd.read_csv("train.csv")

FEATURE_GROUPS = [
    ("Performance & Battery", ["ram", "int_memory", "battery_power"]),
    ("Display & Dimensions", ["px_width", "px_height", "sc_w", "sc_h", "touch_screen"]),
    ("Camera & Build", ["pc", "mobile_wt"]),
]

# ---------------------------------------------------------------------------
# Header (Compact)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="page-header">
        <div class="header-left">
            <div class="phone-mark">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="6" y="2" width="12" height="20" rx="2.5"></rect>
                    <line x1="10" y1="5" x2="14" y2="5"></line>
                    <circle cx="12" cy="18.5" r="0.8" fill="#38bdf8"></circle>
                </svg>
            </div>
            <div>
                <h1 class="page-title">Mobile Phone Price Predictor</h1>
                <p class="page-subtitle">Enter device specifications to estimate its price tier.</p>
            </div>
        </div>
        <div class="header-meta">4 Price Tiers · Spec Estimator</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Main 2-Column Layout
# ---------------------------------------------------------------------------
col_form, col_preview = st.columns([1.35, 1], gap="large")

with col_form:
    with st.container(border=True, key="form_card"):
        input_data = {}
        rendered_features = set()

        def render_feature_input(feature_name: str) -> float:
            train_min = float(df[feature_name].min())
            train_max = float(df[feature_name].max())
            average = float(df[feature_name].median())

            label_name, unit = FEATURE_META.get(
                feature_name, (feature_name.replace("_", " ").title(), "")
            )

            # Sensible physical bounds: prevent negative values; use toggle for binary touch_screen.
            # Do not clamp continuous specs to train_max so users can enter modern values (e.g. 4500 MB RAM)
            # and receive a clear out-of-range warning instead of a hard widget error.
            if feature_name == "touch_screen":
                toggled = st.toggle(
                    label_name,
                    value=bool(average >= 0.5),
                    help=f"Trained range: {train_min:.0f} (No) – {train_max:.0f} (Yes)",
                    key=f"input_{feature_name}",
                )
                return 1.0 if toggled else 0.0

            return st.number_input(
                label_name,
                min_value=0.0,
                value=average,
                help=f"Trained range: {train_min:.0f} – {train_max:.0f}" + (f" {unit}" if unit else ""),
                key=f"input_{feature_name}",
            )

        def render_group_grid(features_list: list[str]) -> None:
            # Pair features 2-per-row; if an odd number of features exist, span the last one full-width.
            pair_count = (len(features_list) // 2) * 2
            if pair_count > 0:
                cols = st.columns(2)
                for idx, feature in enumerate(features_list[:pair_count]):
                    with cols[idx % 2]:
                        input_data[feature] = render_feature_input(feature)
                    rendered_features.add(feature)
            if len(features_list) % 2 == 1:
                last_feature = features_list[-1]
                input_data[last_feature] = render_feature_input(last_feature)
                rendered_features.add(last_feature)

        for group_title, group_features in FEATURE_GROUPS:
            active_in_group = [f for f in group_features if f in selected_features]
            if not active_in_group:
                continue

            st.markdown(f'<div class="group-title">{group_title}</div>', unsafe_allow_html=True)
            render_group_grid(active_in_group)

        remaining = [f for f in selected_features if f not in rendered_features]
        if remaining:
            st.markdown('<div class="group-title">Additional Specifications</div>', unsafe_allow_html=True)
            render_group_grid(remaining)

        submitted = st.button("Predict Price Range", use_container_width=True)

# Preserve exact feature order expected by scaler & model
ordered_input_data = {feature: input_data[feature] for feature in selected_features}

# Validate inputs against the training dataset's supported range
out_of_range_details = []
for feature in selected_features:
    train_min = float(df[feature].min())
    train_max = float(df[feature].max())
    val = float(ordered_input_data[feature])
    if val < train_min or val > train_max:
        label_name, unit = FEATURE_META.get(
            feature, (feature.replace("_", " ").title(), "")
        )
        unit_suffix = f" {unit}" if unit and feature != "touch_screen" else ""
        out_of_range_details.append(
            f"**{label_name}** (`{val:g}{unit_suffix}` entered; model trained on `{train_min:g}`–`{train_max:g}{unit_suffix}`)"
        )

if out_of_range_details:
    st.warning(
        "Some specifications are outside the training dataset's supported range. "
        "The model has not been trained on these values, so the prediction may be less reliable:\n- "
        + "\n- ".join(out_of_range_details)
    )

# Blue scale gradient for tiers (Low -> Very High)
TIER_COLORS = {
    0: ("#7dd3fc", 1),
    1: ("#38bdf8", 2),
    2: ("#0ea5e9", 3),
    3: ("#0284c7", 4),
}

PRICE_LABELS = {
    0: "Low Cost",
    1: "Medium Cost",
    2: "High Cost",
    3: "Very High Cost",
}

prediction = None
input_values = None
prob_by_class = None
highest_confidence = None

if submitted:
    input_df = pd.DataFrame([ordered_input_data])

    if scaler is not None:
        input_values = scaler.transform(input_df)
    else:
        input_values = input_df

    prediction = model.predict(input_values)[0]

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(input_values)[0]
        if hasattr(model, "classes_"):
            prob_by_class = {int(cls): float(prob) for cls, prob in zip(model.classes_, probabilities)}
        else:
            prob_by_class = {idx: float(prob) for idx, prob in enumerate(probabilities)}
        highest_confidence = max(prob_by_class.values())

with col_preview:
    touch_text = "Yes" if ordered_input_data.get("touch_screen", 0) >= 0.5 else "No"
    batt_val = ordered_input_data.get("battery_power", 0)
    batt_pct = max(8, min(100, int(batt_val / 2000.0 * 100)))
    ram_val = ordered_input_data.get("ram", 0)

    if submitted:
        price_labels = PRICE_LABELS
        accent_color, level = TIER_COLORS[int(prediction)]
        steps_html = "".join(
            f'<div class="tier-step" style="background:{TIER_COLORS[i][0] if i < level else "#1e293b"};"></div>'
            for i in range(4)
        )
        confidence_subline = (
            f'<div style="margin-top:0.35rem; font-size:0.86rem; font-weight:500; color:#cbd5e1;">'
            f'Confidence: <span class="mono-num" style="color:{accent_color}; font-weight:600;">{highest_confidence * 100.0:.1f}%</span>'
            f'</div>'
            if highest_confidence is not None
            else ""
        )

        st.markdown(
            f"""
            <div class="phone-chassis">
                <div class="phone-screen">
                    <div class="phone-status-bar">
                        <span>SIM1 · SIM2 5G</span>
                        <div class="dynamic-island"></div>
                        <span class="batt-pill">
                            <span class="batt-icon"><span class="batt-fill" style="width:{batt_pct}%;"></span></span>
                            {batt_val:.0f}mAh
                        </span>
                    </div>
                    <div class="price-readout" style="border-color: {accent_color};">
                        <div class="price-label">Predicted Price Range</div>
                        <p class="price-value" style="color: {accent_color};">{price_labels[prediction]}</p>
                        {confidence_subline}
                        <div class="tier-steps">{steps_html}</div>
                    </div>
                    <div class="hw-tiles">
                        <div class="hw-tile">
                            <div class="hw-tile-label">RAM Module</div>
                            <div class="hw-tile-val">{ram_val:.0f} MB</div>
                        </div>
                        <div class="hw-tile">
                            <div class="hw-tile-label">Battery Power</div>
                            <div class="hw-tile-val">{batt_val:.0f} mAh</div>
                        </div>
                    </div>
                    <table class="spec-table">
                        <tr><td class="spec-key">RAM</td><td class="spec-val">{ordered_input_data.get('ram', 0):.0f} MB</td></tr>
                        <tr><td class="spec-key">Storage</td><td class="spec-val">{ordered_input_data.get('int_memory', 0):.0f} GB</td></tr>
                        <tr><td class="spec-key">Display</td><td class="spec-val">{ordered_input_data.get('px_width', 0):.0f} × {ordered_input_data.get('px_height', 0):.0f} px</td></tr>
                        <tr><td class="spec-key">Size</td><td class="spec-val">{ordered_input_data.get('sc_w', 0):.1f} × {ordered_input_data.get('sc_h', 0):.1f} cm</td></tr>
                        <tr><td class="spec-key">Camera</td><td class="spec-val">{ordered_input_data.get('pc', 0):.0f} MP</td></tr>
                        <tr><td class="spec-key">Weight</td><td class="spec-val">{ordered_input_data.get('mobile_wt', 0):.0f} g</td></tr>
                        <tr><td class="spec-key">Touch Screen</td><td class="spec-val">{touch_text}</td></tr>
                    </table>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if prob_by_class is not None and highest_confidence is not None:
            ordered_categories = ["Low Cost", "Medium Cost", "High Cost", "Very High Cost"]
            ordered_probs_pct = [prob_by_class[idx] * 100.0 for idx in range(4)]
            pred_idx = int(prediction)

            rows_html = ""
            for idx, (name, pct) in enumerate(zip(ordered_categories, ordered_probs_pct)):
                is_pred = idx == pred_idx
                bar_color = accent_color if is_pred else "#475569"
                label_weight = "600" if is_pred else "400"
                label_color = "#f8fafc" if is_pred else "#cbd5e1"
                rows_html += (
                    f'<div class="prob-row">'
                    f'<div class="prob-meta" style="font-weight:{label_weight}; color:{label_color};">'
                    f'<span>{name}</span><span class="prob-pct">{pct:.1f}%</span>'
                    f'</div>'
                    f'<div class="prob-bar-bg"><div class="prob-bar-fill" style="width:{pct:.1f}%; background:{bar_color};"></div></div>'
                    f'</div>'
                )

            tooltip_text = (
                "Model confidence is the estimated probability for each price tier; "
                "it does not guarantee prediction accuracy."
            )
            st.markdown(
                f"""
                <div class="confidence-box">
                    <div class="confidence-header">
                        <span>Prediction Confidence</span>
                        <span class="info-tip" title="{tooltip_text}">i</span>
                    </div>
                    {rows_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

            if out_of_range_details:
                st.info(
                    "Note: Because one or more inputs are outside the training dataset's supported range, "
                    "the model's confidence score should not be interpreted as a guarantee of prediction accuracy."
                )
    else:
        st.markdown(
            f"""
            <div class="phone-chassis">
                <div class="phone-screen">
                    <div class="phone-status-bar">
                        <span>SIM1 · SIM2 5G</span>
                        <div class="dynamic-island"></div>
                        <span class="batt-pill">
                            <span class="batt-icon"><span class="batt-fill" style="width:{batt_pct}%;"></span></span>
                            {batt_val:.0f}mAh
                        </span>
                    </div>
                    <div class="price-readout price-readout-empty">
                        <div class="price-label">Ready to Predict</div>
                        <p class="price-value" style="font-size: 1.05rem; font-weight: 500; color: #cbd5e1;">
                            Enter specs and press Predict
                        </p>
                        <div class="tier-steps">
                            <div class="tier-step"></div>
                            <div class="tier-step"></div>
                            <div class="tier-step"></div>
                            <div class="tier-step"></div>
                        </div>
                    </div>
                    <div class="hw-tiles">
                        <div class="hw-tile">
                            <div class="hw-tile-label">RAM Module</div>
                            <div class="hw-tile-val">{ram_val:.0f} MB</div>
                        </div>
                        <div class="hw-tile">
                            <div class="hw-tile-label">Battery Power</div>
                            <div class="hw-tile-val">{batt_val:.0f} mAh</div>
                        </div>
                    </div>
                    <table class="spec-table">
                        <tr><td class="spec-key">RAM</td><td class="spec-val">{ordered_input_data.get('ram', 0):.0f} MB</td></tr>
                        <tr><td class="spec-key">Storage</td><td class="spec-val">{ordered_input_data.get('int_memory', 0):.0f} GB</td></tr>
                        <tr><td class="spec-key">Display</td><td class="spec-val">{ordered_input_data.get('px_width', 0):.0f} × {ordered_input_data.get('px_height', 0):.0f} px</td></tr>
                        <tr><td class="spec-key">Size</td><td class="spec-val">{ordered_input_data.get('sc_w', 0):.1f} × {ordered_input_data.get('sc_h', 0):.1f} cm</td></tr>
                        <tr><td class="spec-key">Camera</td><td class="spec-val">{ordered_input_data.get('pc', 0):.0f} MP</td></tr>
                        <tr><td class="spec-key">Weight</td><td class="spec-val">{ordered_input_data.get('mobile_wt', 0):.0f} g</td></tr>
                        <tr><td class="spec-key">Touch Screen</td><td class="spec-val">{touch_text}</td></tr>
                    </table>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Hardware Telemetry & Market Analytics Section (Visual Insights)
# ---------------------------------------------------------------------------
def build_spec_radar_svg(user_vals: dict, benchmark_vals: dict, benchmark_label: str) -> str:
    """Render a glowing cyan HUD hexagonal radar comparing device specs against a benchmark."""
    axes = [
        ("RAM", "ram", f"{user_vals['ram']:.0f} MB"),
        ("Battery", "battery_power", f"{user_vals['battery_power']:.0f} mAh"),
        ("Storage", "int_memory", f"{user_vals['int_memory']:.0f} GB"),
        ("Pixels", "px_area", f"{user_vals['px_area'] / 1e6:.2f} MPx"),
        ("Camera", "pc", f"{user_vals['pc']:.0f} MP"),
        ("Screen", "sc_area", f"{user_vals['sc_area']:.0f} cm²"),
    ]

    min_bounds = {
        "ram": float(df["ram"].min()),
        "battery_power": float(df["battery_power"].min()),
        "int_memory": float(df["int_memory"].min()),
        "px_area": float((df["px_width"] * df["px_height"]).min()),
        "pc": float(df["pc"].min()),
        "sc_area": float((df["sc_w"] * df["sc_h"]).min()),
    }
    max_bounds = {
        "ram": float(df["ram"].max()),
        "battery_power": float(df["battery_power"].max()),
        "int_memory": float(df["int_memory"].max()),
        "px_area": float((df["px_width"] * df["px_height"]).max()),
        "pc": float(df["pc"].max()),
        "sc_area": float((df["sc_w"] * df["sc_h"]).max()),
    }

    def norm(key: str, val: float) -> float:
        span = max(1e-6, max_bounds[key] - min_bounds[key])
        return max(0.06, min(1.0, (val - min_bounds[key]) / span))

    cx, cy, radius = 175.0, 138.0, 90.0
    n = len(axes)

    rings_svg = ""
    for frac in (0.25, 0.5, 0.75, 1.0):
        pts = []
        for i in range(n):
            angle = -math.pi / 2 + 2 * math.pi * i / n
            pts.append(f"{cx + radius * frac * math.cos(angle):.1f},{cy + radius * frac * math.sin(angle):.1f}")
        stroke_op = "0.32" if frac == 1.0 else "0.14"
        rings_svg += (
            f'<polygon points="{" ".join(pts)}" fill="none" '
            f'stroke="rgba(56,189,248,{stroke_op})" stroke-width="1"/>'
        )

    spokes_svg = ""
    labels_svg = ""
    user_pts = []
    bench_pts = []
    dots_svg = ""

    for i, (title, key, disp_val) in enumerate(axes):
        angle = -math.pi / 2 + 2 * math.pi * i / n
        cos_a, sin_a = math.cos(angle), math.sin(angle)

        x_end = cx + radius * cos_a
        y_end = cy + radius * sin_a
        spokes_svg += (
            f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x_end:.1f}" y2="{y_end:.1f}" '
            f'stroke="rgba(56,189,248,0.18)" stroke-width="1"/>'
        )

        u_r = radius * norm(key, user_vals[key])
        b_r = radius * norm(key, benchmark_vals[key])
        ux, uy = cx + u_r * cos_a, cy + u_r * sin_a
        bx, by = cx + b_r * cos_a, cy + b_r * sin_a
        user_pts.append(f"{ux:.1f},{uy:.1f}")
        bench_pts.append(f"{bx:.1f},{by:.1f}")
        dots_svg += (
            f'<circle cx="{ux:.1f}" cy="{uy:.1f}" r="4" fill="#38bdf8" '
            f'stroke="#f8fafc" stroke-width="1.3"/>'
        )

        lx = cx + (radius + 22) * cos_a
        ly = cy + (radius + 19) * sin_a
        anchor = "middle" if abs(cos_a) < 0.25 else ("start" if cos_a > 0 else "end")
        dy_title = -3 if sin_a <= 0 else 4
        labels_svg += (
            f'<text x="{lx:.1f}" y="{ly + dy_title:.1f}" text-anchor="{anchor}" '
            f'fill="#e2e8f0" font-family="DM Sans, sans-serif" font-size="11" font-weight="600">{title}</text>'
            f'<text x="{lx:.1f}" y="{ly + dy_title + 12:.1f}" text-anchor="{anchor}" '
            f'fill="#7dd3fc" font-family="JetBrains Mono, monospace" font-size="9.5">{disp_val}</text>'
        )

    return f"""
    <div class="radar-wrap">
        <svg viewBox="0 0 350 280" width="100%" style="max-width: 380px; height: auto;">
            <defs>
                <filter id="cyanGlow" x="-30%" y="-30%" width="160%" height="160%">
                    <feGaussianBlur stdDeviation="3.5" result="blur"/>
                    <feMerge>
                        <feMergeNode in="blur"/>
                        <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                </filter>
            </defs>
            {rings_svg}
            {spokes_svg}
            <polygon points="{' '.join(bench_pts)}" fill="rgba(148,163,184,0.10)"
                     stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4 3"/>
            <polygon points="{' '.join(user_pts)}" fill="rgba(56,189,248,0.24)"
                     stroke="#38bdf8" stroke-width="2.2" filter="url(#cyanGlow)"/>
            {dots_svg}
            {labels_svg}
        </svg>
        <div class="radar-legend">
            <span class="radar-legend-item">
                <span style="width:10px;height:10px;border-radius:2px;background:#38bdf8;display:inline-block;"></span>
                Your Device
            </span>
            <span class="radar-legend-item">
                <span style="width:14px;height:0;border-top:2px dashed #94a3b8;display:inline-block;"></span>
                {benchmark_label}
            </span>
        </div>
    </div>
    """


active_tier_badge = (
    f"Active Telemetry · {PRICE_LABELS[int(prediction)]}"
    if submitted and prediction is not None
    else "Live Spec Telemetry · 2,000 Reference Devices"
)

st.markdown(
    f"""
    <div class="analytics-banner">
        <div class="analytics-title-wrap">
            <span class="telemetry-dot"></span>
            <div>
                <h2 class="analytics-title">Hardware Telemetry &amp; Market Analytics</h2>
                <p class="analytics-sub">Compare your hardware profile, market positioning, and model decision drivers in real time.</p>
            </div>
        </div>
        <div class="header-meta">{active_tier_badge}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

tier_domain = ["Low Cost", "Medium Cost", "High Cost", "Very High Cost"]
tier_range = ["#bae6fd", "#38bdf8", "#0284c7", "#1d4ed8"]

user_radar_vals = {
    "ram": float(ordered_input_data.get("ram", 0)),
    "battery_power": float(ordered_input_data.get("battery_power", 0)),
    "int_memory": float(ordered_input_data.get("int_memory", 0)),
    "px_area": float(ordered_input_data.get("px_width", 0)) * float(ordered_input_data.get("px_height", 0)),
    "pc": float(ordered_input_data.get("pc", 0)),
    "sc_area": float(ordered_input_data.get("sc_w", 0)) * float(ordered_input_data.get("sc_h", 0)),
}

if submitted and prediction is not None:
    bench_df = df[df["price_range"] == int(prediction)]
    bench_label = f"{PRICE_LABELS[int(prediction)]} Avg"
else:
    bench_df = df
    bench_label = "Market Median"

bench_radar_vals = {
    "ram": float(bench_df["ram"].median()),
    "battery_power": float(bench_df["battery_power"].median()),
    "int_memory": float(bench_df["int_memory"].median()),
    "px_area": float((bench_df["px_width"] * bench_df["px_height"]).median()),
    "pc": float(bench_df["pc"].median()),
    "sc_area": float((bench_df["sc_w"] * bench_df["sc_h"]).median()),
}

row1_col1, row1_col2 = st.columns([1.0, 1.25], gap="large")

with row1_col1:
    with st.container(border=True, key="card_radar"):
        st.markdown(
            '<div class="chart-head"><span class="chart-title">Hardware Spec Radar</span></div>'
            '<div class="chart-sub">Normalized profile across 6 core specs vs. benchmark.</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            build_spec_radar_svg(user_radar_vals, bench_radar_vals, bench_label),
            unsafe_allow_html=True,
        )

with row1_col2:
    with st.container(border=True, key="card_market"):
        st.markdown(
            '<div class="chart-head"><span class="chart-title">Market Map · RAM vs Battery</span></div>'
            '<div class="chart-sub">Your device pinned over 2,000 training phones colored by price tier.</div>',
            unsafe_allow_html=True,
        )
        scatter_df = df[["ram", "battery_power", "int_memory", "pc", "price_range"]].copy()
        scatter_df["Price Tier"] = scatter_df["price_range"].map(PRICE_LABELS)

        user_pin_df = pd.DataFrame(
            [
                {
                    "ram": float(ordered_input_data.get("ram", 0)),
                    "battery_power": float(ordered_input_data.get("battery_power", 0)),
                    "Label": "Your Device",
                }
            ]
        )

        cloud = (
            alt.Chart(scatter_df)
            .mark_circle(size=34, opacity=0.52)
            .encode(
                x=alt.X(
                    "ram:Q",
                    title="RAM (MB)",
                    axis=alt.Axis(labelColor="#cbd5e1", titleColor="#94a3b8", gridColor="rgba(56,189,248,0.10)"),
                ),
                y=alt.Y(
                    "battery_power:Q",
                    title="Battery Capacity (mAh)",
                    axis=alt.Axis(labelColor="#cbd5e1", titleColor="#94a3b8", gridColor="rgba(56,189,248,0.10)"),
                ),
                color=alt.Color(
                    "Price Tier:N",
                    scale=alt.Scale(domain=tier_domain, range=tier_range),
                    legend=alt.Legend(
                        orient="top",
                        title=None,
                        labelColor="#cbd5e1",
                        labelFontSize=11,
                        symbolSize=80,
                    ),
                ),
                tooltip=[
                    alt.Tooltip("Price Tier:N", title="Tier"),
                    alt.Tooltip("ram:Q", title="RAM (MB)", format=".0f"),
                    alt.Tooltip("battery_power:Q", title="Battery (mAh)", format=".0f"),
                    alt.Tooltip("int_memory:Q", title="Storage (GB)", format=".0f"),
                    alt.Tooltip("pc:Q", title="Camera (MP)", format=".0f"),
                ],
            )
        )

        vline = (
            alt.Chart(user_pin_df)
            .mark_rule(color="#38bdf8", strokeDash=[4, 4], opacity=0.75)
            .encode(x="ram:Q")
        )
        hline = (
            alt.Chart(user_pin_df)
            .mark_rule(color="#38bdf8", strokeDash=[4, 4], opacity=0.75)
            .encode(y="battery_power:Q")
        )
        pin = (
            alt.Chart(user_pin_df)
            .mark_point(shape="diamond", size=230, filled=True, fill="#ffffff", stroke="#38bdf8", strokeWidth=2.5)
            .encode(
                x="ram:Q",
                y="battery_power:Q",
                tooltip=[
                    alt.Tooltip("Label:N", title="Target"),
                    alt.Tooltip("ram:Q", title="RAM (MB)", format=".0f"),
                    alt.Tooltip("battery_power:Q", title="Battery (mAh)", format=".0f"),
                ],
            )
        )

        market_chart = (
            (cloud + vline + hline + pin)
            .properties(height=285, background="transparent")
            .configure_view(strokeWidth=0)
        )
        st.altair_chart(market_chart, width="stretch")

row2_col1, row2_col2 = st.columns(2, gap="large")

with row2_col1:
    with st.container(border=True, key="card_drivers"):
        if submitted and prediction is not None and hasattr(model, "coef_") and input_values is not None:
            pred_cls = int(prediction)
            cls_idx = list(model.classes_).index(pred_cls) if hasattr(model, "classes_") else pred_cls
            scaled_arr = input_values.to_numpy()[0] if hasattr(input_values, "to_numpy") else input_values[0]
            contribs = model.coef_[cls_idx] * scaled_arr

            driver_df = pd.DataFrame(
                [
                    {
                        "Feature": FEATURE_META.get(f, (f, ""))[0],
                        "Impact": float(val),
                        "Direction": "Supports Tier" if val >= 0 else "Opposes Tier",
                    }
                    for f, val in zip(selected_features, contribs)
                ]
            )
            driver_df["AbsImpact"] = driver_df["Impact"].abs()
            driver_df = driver_df.sort_values("AbsImpact", ascending=False)

            st.markdown(
                '<div class="chart-head"><span class="chart-title">Decision Drivers</span></div>'
                f'<div class="chart-sub">Log-odds contribution of each spec toward <b>{PRICE_LABELS[pred_cls]}</b>.</div>',
                unsafe_allow_html=True,
            )

            zero_line = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color="rgba(148,163,184,0.45)").encode(x="x:Q")
            driver_bars = (
                alt.Chart(driver_df)
                .mark_bar(cornerRadiusEnd=4, height=16)
                .encode(
                    y=alt.Y(
                        "Feature:N",
                        sort=alt.EncodingSortField(field="AbsImpact", order="descending"),
                        title=None,
                        axis=alt.Axis(labelColor="#e2e8f0", labelLimit=130),
                    ),
                    x=alt.X(
                        "Impact:Q",
                        title="Model Contribution (Log-Odds)",
                        axis=alt.Axis(labelColor="#cbd5e1", titleColor="#94a3b8", gridColor="rgba(56,189,248,0.10)"),
                    ),
                    color=alt.Color(
                        "Direction:N",
                        scale=alt.Scale(domain=["Supports Tier", "Opposes Tier"], range=["#38bdf8", "#64748b"]),
                        legend=alt.Legend(orient="top", title=None, labelColor="#cbd5e1"),
                    ),
                    tooltip=[
                        alt.Tooltip("Feature:N", title="Spec"),
                        alt.Tooltip("Impact:Q", title="Contribution", format="+.2f"),
                    ],
                )
            )
            driver_chart = (
                (driver_bars + zero_line)
                .properties(height=275, background="transparent")
                .configure_view(strokeWidth=0)
            )
            st.altair_chart(driver_chart, width="stretch")
        else:
            st.markdown(
                '<div class="chart-head"><span class="chart-title">Model Feature Weights</span></div>'
                '<div class="chart-sub">Overall spec sensitivity across tiers (press Predict for per-spec drivers).</div>',
                unsafe_allow_html=True,
            )
            if hasattr(model, "coef_"):
                mean_weights = abs(model.coef_).mean(axis=0)
                weight_df = pd.DataFrame(
                    [
                        {"Feature": FEATURE_META.get(f, (f, ""))[0], "Weight": float(w)}
                        for f, w in zip(selected_features, mean_weights)
                    ]
                ).sort_values("Weight", ascending=False)
                weight_chart = (
                    alt.Chart(weight_df)
                    .mark_bar(cornerRadiusEnd=4, height=16, color="#38bdf8")
                    .encode(
                        y=alt.Y(
                            "Feature:N",
                            sort=alt.EncodingSortField(field="Weight", order="descending"),
                            title=None,
                            axis=alt.Axis(labelColor="#e2e8f0", labelLimit=130),
                        ),
                        x=alt.X(
                            "Weight:Q",
                            title="Mean |Coefficient| Influence",
                            axis=alt.Axis(labelColor="#cbd5e1", titleColor="#94a3b8", gridColor="rgba(56,189,248,0.10)"),
                        ),
                        tooltip=[
                            alt.Tooltip("Feature:N", title="Spec"),
                            alt.Tooltip("Weight:Q", title="Mean |Coef|", format=".2f"),
                        ],
                    )
                    .properties(height=275, background="transparent")
                    .configure_view(strokeWidth=0)
                )
                st.altair_chart(weight_chart, width="stretch")

with row2_col2:
    with st.container(border=True, key="card_ram"):
        st.markdown(
            '<div class="chart-head"><span class="chart-title">RAM Spectrum by Price Tier</span></div>'
            '<div class="chart-sub">Smooth RAM density across tiers with your entered RAM highlighted.</div>',
            unsafe_allow_html=True,
        )
        ram_dist_df = df[["ram", "price_range"]].copy()
        ram_dist_df["Price Tier"] = ram_dist_df["price_range"].map(PRICE_LABELS)

        ram_density = (
            alt.Chart(ram_dist_df)
            .transform_density(
                "ram",
                as_=["RAM (MB)", "Density"],
                groupby=["Price Tier"],
                extent=[float(df["ram"].min()), float(df["ram"].max())],
            )
            .mark_area(opacity=0.28, interpolate="monotone", line={"strokeWidth": 2})
            .encode(
                x=alt.X(
                    "RAM (MB):Q",
                    title="RAM (MB)",
                    axis=alt.Axis(labelColor="#cbd5e1", titleColor="#94a3b8", gridColor="rgba(56,189,248,0.10)"),
                ),
                y=alt.Y(
                    "Density:Q",
                    title="Relative Density",
                    axis=alt.Axis(labels=False, ticks=False, titleColor="#94a3b8", gridColor="rgba(56,189,248,0.08)"),
                ),
                color=alt.Color(
                    "Price Tier:N",
                    scale=alt.Scale(domain=tier_domain, range=tier_range),
                    legend=alt.Legend(orient="top", title=None, labelColor="#cbd5e1", labelFontSize=11),
                ),
                tooltip=[
                    alt.Tooltip("Price Tier:N", title="Tier"),
                    alt.Tooltip("RAM (MB):Q", title="RAM (MB)", format=".0f"),
                ],
            )
        )

        ram_pin_df = pd.DataFrame([{"ram": float(ordered_input_data.get("ram", 0))}])
        ram_rule = (
            alt.Chart(ram_pin_df)
            .mark_rule(color="#f8fafc", strokeWidth=2, strokeDash=[5, 4])
            .encode(x="ram:Q")
        )
        ram_tag = (
            alt.Chart(ram_pin_df)
            .mark_text(text="Your RAM", align="left", dx=6, color="#f8fafc", fontSize=11, fontWeight="bold")
            .encode(x="ram:Q", y=alt.value(14))
        )

        ram_chart = (
            (ram_density + ram_rule + ram_tag)
            .properties(height=275, background="transparent")
            .configure_view(strokeWidth=0)
        )
        st.altair_chart(ram_chart, width="stretch")
