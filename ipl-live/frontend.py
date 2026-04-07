import streamlit as st
import requests

# API URL (change if deployed)
API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(page_title="IPL Win Predictor", layout="centered")

st.title("🏏 IPL Win Probability Predictor")

st.markdown("Enter match situation")

# ── Inputs ─────────────────────────────
batting_team = st.selectbox("Batting Team", [
    "CSK","MI","RCB","KKR","SRH","DC","PBKS","RR","GT","LSG"
])

bowling_team = st.selectbox("Bowling Team", [
    "CSK","MI","RCB","KKR","SRH","DC","PBKS","RR","GT","LSG"
])

venue = st.text_input("Venue", "m_chinnaswamy_stadium")

runs_to_win = st.number_input("Runs to Win", min_value=1, value=50)
balls_remaining = st.number_input("Balls Remaining", min_value=1, max_value=120, value=30)
wickets_remaining = st.number_input("Wickets Remaining", min_value=0, max_value=10, value=7)
first_inning_total = st.number_input("First Innings Total", min_value=50, value=180)

# ── Predict Button ─────────────────────
if st.button("Predict"):
    payload = {
        "batting_team": batting_team,
        "bowling_team": bowling_team,
        "venue": venue,
        "runs_to_win": runs_to_win,
        "balls_remaining": balls_remaining,
        "wickets_remaining": wickets_remaining,
        "first_inning_total": first_inning_total
    }

    try:
        response = requests.post(API_URL, json=payload)

        if response.status_code == 200:
            data = response.json()

            st.subheader("📊 Predictions")

            def show_model(name, model_data):
                st.write(f"### {name}")
                st.write(f"Batting Win %: {model_data['batting_team_win']*100:.2f}%")
                st.write(f"Bowling Win %: {model_data['bowling_team_win']*100:.2f}%")
                st.write(f"🏆 Winner: {model_data['predicted_winner']}")

            show_model("Logistic Regression", data["logistic_regression"])
            show_model("XGBoost", data["xgboost"])
            show_model("CatBoost", data["catboost"])
            show_model("Ensemble (Final)", data["ensemble"])

        else:
            st.error(f"Error: {response.text}")

    except Exception as e:
        st.error(f"API not running: {e}")