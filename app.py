
import streamlit as st
import pandas as pd
import joblib

st.set_page_config(page_title="Mobile Price Predictor", page_icon="📱")

model_bundle = joblib.load("mobile_price_model.pkl")

model = model_bundle['model']
selected_features = model_bundle['selected_features']
scaler = model_bundle['scaler']

st.title("Mobile Phone Price Range Predictor")
st.write("Enter the mobile specifications to predict its price range.")

df = pd.read_csv("train.csv")

with st.form("prediction_form"):
    input_data = {}

    for feature in selected_features:
        minimum = float(df[feature].min())
        maximum = float(df[feature].max())
        average = float(df[feature].median())

        input_data[feature] = st.number_input(
            feature.replace('_', ' ').title(),
            min_value=minimum,
            max_value=maximum,
            value=average
        )

    submitted = st.form_submit_button("Predict Price Range")

if submitted:
    input_df = pd.DataFrame([input_data])
    
    if scaler is not None:
        input_values = scaler.transform(input_df)
    else:
        input_values = input_df

    prediction = model.predict(input_values)[0]

    price_labels = {
        0: "Low Cost",
        1: "Medium Cost",
        2: "High Cost",
        3: "Very High Cost"
    }

    st.success(f"Predicted Price Range: {price_labels[prediction]}")

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(input_values)[0]
        st.subheader("Prediction Confidence")
        st.bar_chart(
            pd.DataFrame({
                "Price Range": ["Low", "Medium", "High", "Very High"],
                "Probability": probabilities
            }).set_index("Price Range")
        )