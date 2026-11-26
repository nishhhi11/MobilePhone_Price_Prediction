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
# Custom Theme: Grounded Smartphone Hardware & Editorial Spec-Sheet Look
# ---------------------------------------------------------------------------
PHONE_PATTERN_SVG = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='260' height='260' viewBox='0 0 260 260'%3E"
    "%3Cg fill='none' stroke='%23ffffff' stroke-opacity='0.055' stroke-width='1.5'%3E"
    "%3Cg transform='translate(28 24) rotate(-14)'%3E"
    "%3Crect x='0' y='0' width='44' height='82' rx='8'/%3E"
    "%3Crect x='14' y='5' width='16' height='3' rx='1.5'/%3E"
    "%3Crect x='5' y='12' width='34' height='58' rx='3'/%3E"
    "%3Ccircle cx='22' cy='75' r='2.5'/%3E"
    "%3C/g%3E"
    "%3Cg transform='translate(168 30) rotate(10)'%3E"
    "%3Crect x='0' y='0' width='42' height='42' rx='10'/%3E"
    "%3Ccircle cx='13' cy='13' r='5.5'/%3E"
    "%3Ccircle cx='29' cy='13' r='5.5'/%3E"
    "%3Ccircle cx='13' cy='29' r='5.5'/%3E"
    "%3Ccircle cx='29' cy='29' r='2.5'/%3E"
    "%3C/g%3E"
    "%3Cg transform='translate(106 112)'%3E"
    "%3Crect x='0' y='4' width='34' height='18' rx='3'/%3E"
    "%3Crect x='34' y='9' width='3' height='8' rx='1'/%3E"
    "%3Crect x='4' y='8' width='10' height='10' rx='1'/%3E"
    "%3Crect x='17' y='8' width='10' height='10' rx='1'/%3E"
    "%3C/g%3E"
    "%3Cg transform='translate(36 164) rotate(12)'%3E"
    "%3Crect x='0' y='0' width='50' height='86' rx='9'/%3E"
    "%3Crect x='6' y='8' width='38' height='68' rx='4'/%3E"
    "%3Crect x='18' y='4' width='14' height='2.5' rx='1'/%3E"
    "%3C/g%3E"
    "%3Cg transform='translate(172 148) rotate(-10)'%3E"
    "%3Crect x='0' y='0' width='46' height='86' rx='8'/%3E"
    "%3Crect x='6' y='6' width='18' height='24' rx='4'/%3E"
    "%3Ccircle cx='15' cy='13' r='3.5'/%3E"
    "%3Ccircle cx='15' cy='23' r='3.5'/%3E"
    "%3C/g%3E"
    "%3Cpath d='M126 42 a12 12 0 0 1 16 0 M122 36 a18 18 0 0 1 24 0'/%3E"
    "%3C/g%3E%3C/svg%3E"
)

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {{
        --bg-base: #121417;
        --bg-surface: #1a1d23;
        --bg-surface-2: #22262e;
        --border-line: #2e333d;
        --text-main: #f3f4f6;
        --text-sub: #9ca3af;
        --brand: #2563eb;
        --brand-hover: #1d4ed8;
    }}

    .stApp {{
        background-color: var(--bg-base);
        background-image:
            linear-gradient(180deg, rgba(18, 20, 23, 0.72) 0%, rgba(18, 20, 23, 0.88) 100%),
            url("{PHONE_PATTERN_SVG}");
        background-repeat: repeat;
        background-size: auto, 260px 260px;
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
        border: 1px solid var(--border-line) !important;
        border-radius: 14px !important;
        padding: 1.25rem 1.4rem !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
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
        background: #1d2026;
        border: 3px solid #343944;
        border-radius: 34px;
        padding: 14px;
        box-shadow: 0 20px 44px rgba(0, 0, 0, 0.48);
        max-width: 390px;
        margin: 0 auto;
    }}

    .phone-screen {{
        background: #121417;
        border: 1px solid #2a2f3a;
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
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e5e7eb" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="6" y="2" width="12" height="20" rx="2.5"></rect>
                    <line x1="10" y1="5" x2="14" y2="5"></line>
                    <circle cx="12" cy="18.5" r="0.8" fill="#e5e7eb"></circle>
                </svg>
            </div>
            <div>
                <h1 class="page-title">Mobile Phone Price Range Predictor</h1>
                <p class="page-subtitle">Enter the mobile specifications to predict its price range.</p>
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
                        <span>5G</span>
                        <div class="dynamic-island"></div>
                        <span>{ordered_input_data.get('battery_power', 0):.0f}mAh</span>
                    </div>
                    <div class="price-readout" style="border-color: {accent_color};">
                        <div class="price-label">Predicted Price Range</div>
                        <p class="price-value" style="color: {accent_color};">{price_labels[prediction]}</p>
                        {confidence_subline}
                        <div class="tier-steps">{steps_html}</div>
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
                .properties(height=270, background="#1a1d23")
                .configure_view(stroke="#2e333d", fill="#1a1d23")
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
                        <span>5G</span>
                        <div class="dynamic-island"></div>
                        <span>{ordered_input_data.get('battery_power', 0):.0f}mAh</span>
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
