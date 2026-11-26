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
# Custom Theme: Deep Teal-Blue PCB / Mobile SoC Circuit Board (Reference UI)
# ---------------------------------------------------------------------------
PCB_PATTERN_SVG = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='360' height='360' viewBox='0 0 360 360'%3E"
    "%3Cdefs%3E"
    "%3ClinearGradient id='traceGlow' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E"
    "%3Cstop offset='0%25' stop-color='%237dd3fc' stop-opacity='0.34'/%3E"
    "%3Cstop offset='50%25' stop-color='%2338bdf8' stop-opacity='0.14'/%3E"
    "%3Cstop offset='100%25' stop-color='%23bae6fd' stop-opacity='0.30'/%3E"
    "%3C/linearGradient%3E"
    "%3C/defs%3E"
    # Radiating PCB bus traces (45-deg & orthogonal)
    "%3Cg fill='none' stroke='url(%23traceGlow)' stroke-width='1.35' stroke-linecap='round' stroke-linejoin='round'%3E"
    # Top-left bus into center SoC
    "%3Cpath d='M0 36 H72 L116 80 V132 M0 46 H66 L108 88 V132 M0 56 H60 L100 96 V132 M18 0 V30 L84 96 V132'/%3E"
    # Top-right bus into center SoC
    "%3Cpath d='M360 40 H282 L238 84 V132 M360 50 H288 L246 92 V132 M360 60 H294 L254 100 V132 M310 0 V32 L262 80 V132'/%3E"
    # Bottom-left bus out of center SoC
    "%3Cpath d='M132 228 V264 L78 318 H0 M140 228 V270 L84 326 H0 M148 228 V276 L90 334 H0 M124 228 V256 L40 340 V360'/%3E"
    # Bottom-right bus out of center SoC
    "%3Cpath d='M228 228 V264 L282 318 H360 M220 228 V270 L276 326 H360 M212 228 V276 L270 334 H360 M236 228 V256 L320 340 V360'/%3E"
    # Horizontal left/right buses
    "%3Cpath d='M0 162 H132 M0 172 H132 M0 182 H132 M0 192 H132'/%3E"
    "%3Cpath d='M228 162 H360 M228 172 H360 M228 182 H360 M228 192 H360'/%3E"
    # Vertical top/bottom buses
    "%3Cpath d='M162 0 V132 M172 0 V132 M182 0 V132 M192 0 V132'/%3E"
    "%3Cpath d='M162 228 V360 M172 228 V360 M182 228 V360 M192 228 V360'/%3E"
    # Serpentine delay lines
    "%3Cpath d='M26 244 h16 v8 h-16 v8 h16 v8 h-16 M294 114 h18 v8 h-18 v8 h18 v8 h-18'/%3E"
    "%3C/g%3E"
    # Central SoC / Mobile Processor Package
    "%3Cg transform='translate(132 132)'%3E"
    "%3Crect x='0' y='0' width='96' height='96' rx='8' fill='%2303101a' fill-opacity='0.78' stroke='%237dd3fc' stroke-opacity='0.38' stroke-width='1.6'/%3E"
    "%3Crect x='14' y='14' width='68' height='68' rx='4' fill='%23061b2b' fill-opacity='0.9' stroke='%2338bdf8' stroke-opacity='0.32' stroke-width='1.2'/%3E"
    "%3Crect x='26' y='26' width='44' height='44' rx='2' fill='none' stroke='%23bae6fd' stroke-opacity='0.28' stroke-dasharray='3 3'/%3E"
    "%3Ctext x='48' y='52' text-anchor='middle' fill='%237dd3fc' fill-opacity='0.35' font-family='monospace' font-size='11' font-weight='bold'%3ESoC%3C/text%3E"
    "%3C/g%3E"
    # Corner SMD IC Chips (RAM, SIM, BATT) & Via Pads
    "%3Cg fill='%23041522' fill-opacity='0.75' stroke='%237dd3fc' stroke-opacity='0.28' stroke-width='1.1'%3E"
    "%3Crect x='34' y='104' width='42' height='28' rx='3'/%3E"
    "%3Crect x='284' y='224' width='44' height='30' rx='3'/%3E"
    "%3Crect x='272' y='22' width='36' height='22' rx='3'/%3E"
    "%3Ccircle cx='88' cy='252' r='6'/%3E"
    "%3Ccircle cx='104' cy='268' r='4'/%3E"
    "%3Ccircle cx='262' cy='102' r='5'/%3E"
    "%3C/g%3E"
    "%3Cg fill='%237dd3fc' fill-opacity='0.26' font-family='monospace' font-size='8' font-weight='bold'%3E"
    "%3Ctext x='44' y='121'%3ERAM%3C/text%3E"
    "%3Ctext x='294' y='242'%3EBATT%3C/text%3E"
    "%3Ctext x='281' y='36'%3ESIM%3C/text%3E"
    "%3C/g%3E"
    "%3C/svg%3E"
)

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {{
        --bg-base: #041826;
        --bg-surface: rgba(6, 28, 44, 0.88);
        --bg-surface-2: rgba(10, 40, 62, 0.90);
        --border-line: rgba(56, 189, 248, 0.26);
        --text-main: #f0f9ff;
        --text-sub: #93c5fd;
        --brand: #0284c7;
        --brand-hover: #0ea5e9;
    }}

    .stApp {{
        background-color: var(--bg-base);
        background-image:
            radial-gradient(circle at 50% 35%, rgba(56, 189, 248, 0.18) 0%, transparent 48%),
            radial-gradient(circle at 15% 20%, rgba(14, 165, 233, 0.14) 0%, transparent 40%),
            radial-gradient(circle at 85% 80%, rgba(56, 189, 248, 0.12) 0%, transparent 42%),
            linear-gradient(180deg, rgba(4, 24, 38, 0.62) 0%, rgba(3, 16, 27, 0.84) 100%),
            url("{PCB_PATTERN_SVG}");
        background-repeat: no-repeat, no-repeat, no-repeat, no-repeat, repeat;
        background-size: auto, auto, auto, auto, 360px 360px;
        color: var(--text-main);
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header[data-testid="stHeader"] {{
        background: transparent;
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1180px;
    }}

    /* Clean Header Bar */
    .page-header {{
        background: var(--bg-surface);
        border: 1px solid var(--border-line);
        border-radius: 14px;
        padding: 1.5rem 1.75rem;
        margin-bottom: 1.4rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.28);
    }}

    .header-left {{
        display: flex;
        align-items: center;
        gap: 1rem;
    }}

    .phone-mark {{
        width: 48px;
        height: 48px;
        border-radius: 12px;
        background: var(--bg-surface-2);
        border: 1px solid #374151;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }}

    .page-title {{
        font-size: 1.65rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0 0 0.2rem 0;
        letter-spacing: -0.02em;
    }}

    .page-subtitle {{
        font-size: 0.94rem;
        color: var(--text-sub);
        margin: 0;
    }}

    .header-meta {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        color: #9ca3af;
        background: var(--bg-surface-2);
        border: 1px solid var(--border-line);
        padding: 0.45rem 0.8rem;
        border-radius: 8px;
        white-space: nowrap;
    }}

    /* Input Panel Card */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: var(--bg-surface);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid var(--border-line) !important;
        border-radius: 14px !important;
        padding: 1.25rem 1.4rem !important;
        box-shadow: 0 12px 32px rgba(2, 12, 22, 0.55), 0 0 24px rgba(14, 165, 233, 0.08);
    }}

    .group-title {{
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #d1d5db;
        margin: 0.65rem 0 0.65rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid var(--border-line);
    }}

    .group-title:first-child {{
        margin-top: 0;
    }}

    div[data-testid="stNumberInput"] label p {{
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        color: #d1d5db !important;
    }}

    div[data-testid="stNumberInput"] input {{
        background-color: var(--bg-base) !important;
        color: #f9fafb !important;
        border: 1px solid #323844 !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.9rem !important;
    }}

    div[data-testid="stNumberInput"] input:focus {{
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }}

    /* Primary Predict Button */
    div.stButton > button {{
        width: 100%;
        margin-top: 0.9rem;
        padding: 0.72rem 1.2rem;
        border-radius: 10px;
        border: 1px solid #3b82f6;
        background: var(--brand);
        color: #ffffff;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.98rem;
        font-weight: 600;
        transition: background-color 0.15s ease, transform 0.12s ease;
    }}

    div.stButton > button:hover {{
        background: var(--brand-hover);
        color: #ffffff;
        transform: translateY(-1px);
    }}

    /* Realistic Smartphone Mockup Preview */
    .phone-chassis {{
        background: linear-gradient(165deg, #0b2538 0%, #05131f 100%);
        border: 2.5px solid rgba(56, 189, 248, 0.35);
        border-radius: 34px;
        padding: 14px;
        box-shadow: 0 20px 44px rgba(2, 12, 22, 0.65), 0 0 28px rgba(14, 165, 233, 0.14);
        max-width: 390px;
        margin: 0 auto;
    }}

    .phone-screen {{
        background: #041421;
        border: 1px solid rgba(56, 189, 248, 0.22);
        border-radius: 24px;
        padding: 1rem 1.1rem 1.2rem 1.1rem;
    }}

    .phone-status-bar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: #9ca3af;
        margin-bottom: 0.85rem;
    }}

    .dynamic-island {{
        width: 78px;
        height: 16px;
        background: #050608;
        border-radius: 999px;
        border: 1px solid #262a33;
    }}

    .price-readout {{
        background: var(--bg-surface);
        border: 1px solid var(--border-line);
        border-radius: 14px;
        padding: 1rem;
        text-align: center;
        margin-bottom: 0.9rem;
    }}

    .price-label {{
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #9ca3af;
        margin-bottom: 0.25rem;
    }}

    .price-value {{
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
    }}

    .tier-steps {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 5px;
        margin-top: 0.75rem;
    }}

    .tier-step {{
        height: 5px;
        border-radius: 999px;
        background: #2b303b;
    }}

    .spec-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.83rem;
    }}

    .spec-table tr {{
        border-bottom: 1px solid #22262e;
    }}

    .spec-table tr:last-child {{
        border-bottom: none;
    }}

    .spec-table td {{
        padding: 0.48rem 0.2rem;
    }}

    .spec-key {{
        color: #9ca3af;
    }}

    .spec-val {{
        text-align: right;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500;
        color: #f3f4f6;
    }}

    .confidence-box {{
        background: var(--bg-surface);
        border: 1px solid var(--border-line);
        border-radius: 14px;
        padding: 1rem 1.15rem;
        margin-top: 1rem;
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
        font-size: 0.82rem;
        color: #d1d5db;
        margin-bottom: 0.2rem;
    }}

    .prob-bar-bg {{
        width: 100%;
        height: 7px;
        border-radius: 999px;
        background: #262b35;
        overflow: hidden;
    }}

    .prob-bar-fill {{
        height: 100%;
        border-radius: 999px;
    }}

    .hw-strip {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.7rem;
    }}

    .hw-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.28rem 0.65rem;
        border-radius: 8px;
        background: var(--bg-surface-2);
        border: 1px solid var(--border-line);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.74rem;
        color: #d1d5db;
    }}

    .hw-tiles {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.55rem;
        margin-bottom: 0.75rem;
    }}

    .hw-tile {{
        background: #181c24;
        border: 1px solid #2b313d;
        border-radius: 10px;
        padding: 0.55rem 0.7rem;
    }}

    .hw-tile-label {{
        font-size: 0.66rem;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #9ca3af;
        margin-bottom: 0.15rem;
    }}

    .hw-tile-val {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.92rem;
        font-weight: 600;
        color: #f3f4f6;
    }}

    .batt-pill {{
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }}

    .batt-icon {{
        width: 24px;
        height: 11px;
        border: 1px solid #6b7280;
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

FEATURE_GROUPS = [
    ("Performance & Battery", ["ram", "int_memory", "battery_power"]),
    ("Display & Dimensions", ["px_width", "px_height", "sc_w", "sc_h", "touch_screen"]),
    ("Camera & Build", ["pc", "mobile_wt"]),
]

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="page-header">
        <div class="header-left">
            <div class="phone-mark">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="6" y="2" width="12" height="20" rx="2.5"></rect>
                    <line x1="10" y1="5" x2="14" y2="5"></line>
                    <circle cx="12" cy="18.5" r="0.8" fill="#60a5fa"></circle>
                </svg>
            </div>
            <div>
                <h1 class="page-title">Mobile Phone Price Range Predictor</h1>
                <p class="page-subtitle">Enter the mobile specifications to predict its price range.</p>
                <div class="hw-strip">
                    <span class="hw-badge">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2"><rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/></svg>
                        RAM &amp; Storage
                    </span>
                    <span class="hw-badge">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><rect x="2" y="7" width="18" height="10" rx="2"/><line x1="22" y1="11" x2="22" y2="13"/><path d="M11 9l-2 3h3l-1 3"/></svg>
                        Battery Power
                    </span>
                    <span class="hw-badge">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2"><path d="M6 2h8l4 4v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z"/><rect x="8" y="11" width="8" height="7" rx="1"/></svg>
                        Dual SIM · 5G
                    </span>
                    <span class="hw-badge">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#c084fc" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
                        Camera &amp; Display
                    </span>
                </div>
            </div>
        </div>
        <div class="header-meta">4 Price Tiers · Hardware Spec Estimator</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Main 2-Column Layout
# ---------------------------------------------------------------------------
col_form, col_preview = st.columns([1.35, 1], gap="large")

with col_form:
    with st.container(border=True):
        input_data = {}
        rendered_features = set()

        def render_feature_input(feature_name: str) -> float:
            train_min = float(df[feature_name].min())
            train_max = float(df[feature_name].max())
            average = float(df[feature_name].median())

            label_name, unit = FEATURE_META.get(
                feature_name, (feature_name.replace("_", " ").title(), "")
            )
            display_label = f"{label_name} ({unit})" if unit else label_name

            # Sensible physical bounds: prevent negative values; restrict binary touch_screen to 0 or 1.
            # Do not clamp continuous specs to train_max so users can enter modern values (e.g. 4500 MB RAM)
            # and receive a clear out-of-range warning instead of a hard widget error.
            if feature_name == "touch_screen":
                return st.number_input(
                    display_label,
                    min_value=0.0,
                    max_value=1.0,
                    value=average,
                    step=1.0,
                    help=f"Trained range: {train_min:.0f} – {train_max:.0f}",
                    key=f"input_{feature_name}",
                )

            return st.number_input(
                display_label,
                min_value=0.0,
                value=average,
                help=f"Trained range: {train_min:.0f} – {train_max:.0f}" + (f" {unit}" if unit else ""),
                key=f"input_{feature_name}",
            )

        for group_title, group_features in FEATURE_GROUPS:
            active_in_group = [f for f in group_features if f in selected_features]
            if not active_in_group:
                continue

            st.markdown(f'<div class="group-title">{group_title}</div>', unsafe_allow_html=True)

            cols = st.columns(2)
            for idx, feature in enumerate(active_in_group):
                with cols[idx % 2]:
                    input_data[feature] = render_feature_input(feature)
                rendered_features.add(feature)

        remaining = [f for f in selected_features if f not in rendered_features]
        if remaining:
            st.markdown('<div class="group-title">Additional Specifications</div>', unsafe_allow_html=True)
            cols = st.columns(2)
            for idx, feature in enumerate(remaining):
                with cols[idx % 2]:
                    input_data[feature] = render_feature_input(feature)

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

TIER_COLORS = {
    0: ("#10b981", 1),
    1: ("#3b82f6", 2),
    2: ("#f59e0b", 3),
    3: ("#ef4444", 4),
}

with col_preview:
    touch_text = "Yes" if ordered_input_data.get("touch_screen", 0) >= 0.5 else "No"
    batt_val = ordered_input_data.get("battery_power", 0)
    batt_pct = max(8, min(100, int(batt_val / 2000.0 * 100)))
    ram_val = ordered_input_data.get("ram", 0)

    if submitted:
        input_df = pd.DataFrame([ordered_input_data])

        if scaler is not None:
            input_values = scaler.transform(input_df)
        else:
            input_values = input_df

        prediction = model.predict(input_values)[0]

        price_labels = {
            0: "Low Cost",
            1: "Medium Cost",
            2: "High Cost",
            3: "Very High Cost",
        }

        prob_by_class = None
        highest_confidence = None
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(input_values)[0]
            if hasattr(model, "classes_"):
                prob_by_class = {int(cls): float(prob) for cls, prob in zip(model.classes_, probabilities)}
            else:
                prob_by_class = {idx: float(prob) for idx, prob in enumerate(probabilities)}
            highest_confidence = max(prob_by_class.values())

        accent_color, level = TIER_COLORS[int(prediction)]
        steps_html = "".join(
            f'<div class="tier-step" style="background:{accent_color if i < level else "#2b303b"};"></div>'
            for i in range(4)
        )
        confidence_subline = (
            f'<div style="margin-top:0.4rem; font-size:0.9rem; font-weight:600; color:#e5e7eb;">'
            f'Model Confidence: <span style="font-family:\'JetBrains Mono\', monospace; color:{accent_color};">{highest_confidence * 100.0:.1f}%</span>'
            f'</div>'
            if highest_confidence is not None
            else ""
        )

        st.markdown(
            f"""
            <div class="phone-chassis">
                <div class="phone-screen">
                    <div class="phone-status-bar">
                        <span>SIM1·SIM2 5G</span>
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
                            <div class="hw-tile-val" style="color:#fbbf24;">{ram_val:.0f} MB</div>
                        </div>
                        <div class="hw-tile">
                            <div class="hw-tile-label">Battery Power</div>
                            <div class="hw-tile-val" style="color:#34d399;">{batt_val:.0f} mAh</div>
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

        st.success(f"Predicted Price Range: {price_labels[prediction]}")

        if prob_by_class is not None and highest_confidence is not None:
            st.progress(
                highest_confidence,
                text=f"Model Confidence ({price_labels[int(prediction)]}): {highest_confidence * 100.0:.1f}%",
            )
            st.caption(
                "Model confidence represents the estimated probability assigned to the predicted price category. "
                "It does not guarantee that the prediction is correct."
            )

            ordered_categories = ["Low Cost", "Medium Cost", "High Cost", "Very High Cost"]
            ordered_probs_pct = [prob_by_class[idx] * 100.0 for idx in range(4)]
            bar_colors = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444"]

            rows_html = ""
            for name, pct, color in zip(ordered_categories, ordered_probs_pct, bar_colors):
                rows_html += (
                    f'<div class="prob-row">'
                    f'<div class="prob-meta"><span>{name}</span><span>{pct:.1f}%</span></div>'
                    f'<div class="prob-bar-bg"><div class="prob-bar-fill" style="width:{pct:.1f}%; background:{color};"></div></div>'
                    f'</div>'
                )

            st.markdown(
                f"""
                <div class="confidence-box">
                    <div class="group-title" style="margin-top:0;">Prediction Confidence</div>
                    {rows_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.subheader("Prediction Confidence")
            chart_df = pd.DataFrame({
                "Price Category": ordered_categories,
                "Confidence (%)": ordered_probs_pct,
                "Label": [f"{pct:.1f}%" for pct in ordered_probs_pct],
            })

            bars = (
                alt.Chart(chart_df)
                .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, size=38)
                .encode(
                    x=alt.X(
                        "Price Category:N",
                        sort=ordered_categories,
                        title="Price Category",
                        axis=alt.Axis(labelAngle=0, labelColor="#d1d5db", titleColor="#9ca3af"),
                    ),
                    y=alt.Y(
                        "Confidence (%):Q",
                        scale=alt.Scale(domain=[0, 100]),
                        title="Confidence (%)",
                        axis=alt.Axis(
                            values=[0, 25, 50, 75, 100],
                            labelExpr="datum.value + '%'",
                            labelColor="#d1d5db",
                            titleColor="#9ca3af",
                            gridColor="#262b35",
                        ),
                    ),
                    color=alt.Color(
                        "Price Category:N",
                        scale=alt.Scale(domain=ordered_categories, range=bar_colors),
                        legend=None,
                    ),
                    tooltip=[
                        alt.Tooltip("Price Category:N", title="Category"),
                        alt.Tooltip("Confidence (%):Q", title="Confidence (%)", format=".1f"),
                    ],
                )
            )

            labels = (
                alt.Chart(chart_df)
                .mark_text(dy=-8, color="#f3f4f6", fontSize=12, fontWeight="bold")
                .encode(
                    x=alt.X("Price Category:N", sort=ordered_categories),
                    y=alt.Y("Confidence (%):Q", scale=alt.Scale(domain=[0, 100])),
                    text="Label:N",
                )
            )

            confidence_chart = (
                (bars + labels)
                .properties(height=270, background="#061c2c")
                .configure_view(stroke="#164e63", fill="#061c2c")
            )
            st.altair_chart(confidence_chart, use_container_width=True)

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
                        <span>SIM1·SIM2 5G</span>
                        <div class="dynamic-island"></div>
                        <span class="batt-pill">
                            <span class="batt-icon"><span class="batt-fill" style="width:{batt_pct}%;"></span></span>
                            {batt_val:.0f}mAh
                        </span>
                    </div>
                    <div class="price-readout">
                        <div class="price-label">Estimated Tier</div>
                        <p class="price-value" style="font-size: 1.15rem; color: #d1d5db;">Submit Specs to Predict</p>
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
                            <div class="hw-tile-val" style="color:#fbbf24;">{ram_val:.0f} MB</div>
                        </div>
                        <div class="hw-tile">
                            <div class="hw-tile-label">Battery Power</div>
                            <div class="hw-tile-val" style="color:#34d399;">{batt_val:.0f} mAh</div>
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
