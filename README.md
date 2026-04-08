# 🏏 IPL Live Win Predictor

> Ball-by-ball win probability engine for IPL second innings — powered by an ensemble of Logistic Regression, XGBoost, and CatBoost trained on **279,587 deliveries** from **IPL 2008–2026**.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red?logo=streamlit)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0+-orange)
![CatBoost](https://img.shields.io/badge/CatBoost-1.2+-yellow)
![License](https://img.shields.io/badge/License-MIT-lightgrey)
![Status](https://img.shields.io/badge/Status-Live-brightgreen)

---

## 🌐 Live Demo

| Service | URL |
|---|---|
| 🎯 Streamlit App | [ipl-winner-pedictor.streamlit.app](https://live-ipl-win-predictor.streamlit.app/) |
| ⚡ FastAPI Backend | [ipl-winner-pedictor.onrender.com](https://ipl-winner-pedictor.onrender.com) |
| 📖 API Docs (Swagger) | [ipl-winner-pedictor.onrender.com/docs](https://ipl-winner-pedictor.onrender.com/docs) |

---

## ⚠️ Important — Please Read Before Using

This app is hosted on **Render's free tier**. Here's what to expect:

- 💤 If the app hasn't been used for **15+ minutes**, both the frontend and backend go to **sleep**
- ⏳ On first visit, the app may take **30–60 seconds to wake up** — this is normal
- 🔄 If you see an error or blank screen, **wait 30 seconds and refresh**
- ✅ After the first request, everything works instantly

> **Why does this happen?** Free hosting services spin down idle apps to save resources. The first request wakes them back up.

---

## 📸 Demo

```
Batting Team  ──────────────────────────────────  Bowling Team
    CSK   50 runs | 30 balls | 7 wickets left    RCB
         CRR: 8.12  |  RRR: 10.00  |  Pressure: +1.88
         Phase: Death Overs

  🏆 Predicted Winner: RCB  —  88.5% Win Probability
```

---

## 📌 What This Project Does

Given any live ball-by-ball situation during the IPL second innings, the system predicts **who is going to win** — along with precise win probabilities from three individual ML models and a weighted ensemble.

Users input:
- Both teams (batting + bowling)
- Venue
- Runs to win, balls remaining, wickets in hand
- First innings total

The system auto-computes CRR, RRR, pressure index, match phase, and historical team performance, then returns probability outputs from all models instantly via a **FastAPI backend** and a **Streamlit frontend**.

---

## 🏗️ Architecture

```
┌──────────────────────────────────┐
│         Streamlit UI             │  ← main.py
│  (Live match input + visualizer) │
└──────────────┬───────────────────┘
               │ HTTP POST /predict
               ▼
┌──────────────────────────────────┐
│         FastAPI Backend          │  ← app.py
│  (Feature computation + routing) │
└──────────────┬───────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
  ipl_win_predictor.pkl (joblib bundle)
  ├── preprocessor     (sklearn ColumnTransformer)
  ├── lr_model         (Logistic Regression)
  ├── xgb_model        (XGBoost)
  ├── cat_model        (CatBoost)
  └── match_results    (historical team win rates)
```

---

## 📂 Project Structure

```
ipl-win-predictor/
│
├── backend/
│   ├── app.py                      # FastAPI backend (prediction API)
│   ├── ipl_win_predictor.pkl       # Trained model bundle (joblib)
│   ├── requirements.txt
│   └── runtime.txt                 # Python 3.11.9
│
├── frontend/
│   └── main.py                     # Streamlit frontend (UI)
│
└── notebook/
    └── IPL_Win_Predictor.ipynb     # Full training pipeline (Google Colab)
```

---

## 📦 Dataset

| File | Season Coverage | Rows |
|------|----------------|------|
| `IPL_ball_by_ball_updated.csv` | 2008–2022 | ~230K |
| `deliveries_updated_ipl_upto_2025.csv` | up to 2025 | ~48K |
| `ipl_2024_deliveries.csv` | 2024 | ~17K |
| `ipl_2025_deliveries.csv` | 2025 | ~18K |
| `ipl_2026_deliveries.csv` | 2026 (partial) | ~1.4K |

**Sources:** [dgsports/ipl-ball-by-ball-2008-to-2022](https://www.kaggle.com/datasets/dgsports/ipl-ball-by-ball-2008-to-2022) · [sahiltailor/ipl-2024-ball-by-ball-dataset](https://www.kaggle.com/datasets/sahiltailor/ipl-2024-ball-by-ball-dataset)

**Total after merging & filtering:** `131,902` second-innings rows used for training and evaluation.

**Team standardization handled:**
```
Delhi Daredevils            → DC
Kings XI Punjab             → PBKS
Royal Challengers Bangalore → RCB
Rising Pune Supergiant      → RPS
```

---

## ⚙️ Feature Engineering

All features are computed **ball-by-ball** to simulate real-time prediction. No future data leakage — all career stats use **cumsum → shift(1)** pattern.

### Match-State Features (computed live)

| Feature | Formula / Description |
|---|---|
| `runs_to_win` | Target − runs scored so far |
| `balls_remaining` | 120 − balls bowled |
| `wickets_remaining` | 10 − wickets fallen |
| `curr_run_rate` | (team_runs × 6) / balls_bowled |
| `req_run_rate` | (runs_to_win × 6) / balls_remaining, capped at 36 |
| `crr_rrr_ratio` | CRR / RRR, clipped [0, 10] — >1.0 = batting team ahead |
| `pressure` | RRR − CRR — positive = under pressure |
| `match_phase` | 0=Powerplay (0–5), 1=Middle (6–14), 2=Death (15–19) |
| `first_innings_total` | Total set by batting-first team |

### Historical Team Performance Features (leak-free)

| Feature | Description |
|---|---|
| `batting_team_perf` | Expanding win rate of batting team as chaser (shifted by 1 match) |
| `bowling_team_perf` | Expanding win rate of bowling team as defender (shifted by 1 match) |

### Player Quality Features (Bayesian-Smoothed, leak-free)

| Feature | Smoothing Formula |
|---|---|
| `batting_average` | (career_runs + 50) / (career_outs + 2) |
| `career_strike_rate` | ((career_runs + 100) / (career_balls + 80)) × 100 |
| `exp_bowler_eco` | ((career_runs_conceded + 300) / (career_balls_bowled + 240)) × 6 |
| `exp_bowler_avg` | (career_runs_conceded + 300) / (career_wickets + 10) |

> All career stats are aggregated season-by-season with a **one-season lag** — the model only sees what was known *before* the current season started.

---

## 🧠 Models

### Preprocessing Pipeline
```
Categorical (batting_team, bowling_team, venue) → OneHotEncoder(drop='first', handle_unknown='ignore')
Numeric (9 features)                            → StandardScaler
```

### 1. Logistic Regression
```python
LogisticRegression(C=0.01, class_weight='balanced', solver='liblinear', max_iter=1000)
```
Strong L2 regularization. Used as the conservative baseline.

### 2. XGBoost Classifier
```python
XGBClassifier(
    n_estimators=300, max_depth=3, learning_rate=0.05,
    subsample=0.6, colsample_bytree=0.6,
    reg_lambda=10, reg_alpha=2, min_child_weight=30, gamma=2,
    scale_pos_weight=neg/pos, early_stopping_rounds=30
)
```
Heavily regularized to prevent overfitting on ball-by-ball data.

### 3. CatBoost Classifier
```python
CatBoostClassifier(
    iterations=150, depth=3, learning_rate=0.02,
    l2_leaf_reg=50, random_strength=10, bagging_temperature=2,
    cat_features=['batting_team', 'bowling_team', 'venue']
)
```
Handles categorical features natively — no one-hot encoding needed.

### 4. Ensemble (Final Output)
```
Ensemble = 0.50 × XGBoost + 0.30 × CatBoost + 0.20 × Logistic Regression
```

---

## 📊 Results

### Temporal Train / Test Split
| Split | Seasons | Rows |
|---|---|---|
| Train | 2008–2023 | ~115,266 |
| Test | 2024–2026 | ~16,636 |

> No random shuffling. Strict temporal split simulates real-world deployment.

### Test Set Performance

| Model | Accuracy | F1 | ROC-AUC | Log Loss | Brier |
|---|---|---|---|---|---|
| Logistic Regression | 0.7584 | 0.7233 | 0.8573 | 0.5039 | 0.1636 |
| XGBoost | **0.8077** | 0.7838 | **0.8956** | **0.4355** | **0.1395** |
| CatBoost | 0.7983 | 0.7751 | 0.8814 | 0.4648 | 0.1478 |
| **Ensemble** | **~0.808** | **~0.785** | **~0.896** | — | — |

> XGBoost leads on AUC (0.896) on unseen 2024–26 data — strong generalization given the strict temporal split.

---

## 🚀 How to Run Locally

### 1. Clone & Install
```bash
git clone https://github.com/DeepanshuSharma1607/ipl-winner-pedictor.git
cd ipl-winner-pedictor
pip install -r backend/requirements.txt
```

### 2. Start the FastAPI Backend
```bash
cd backend
uvicorn app:app --host 127.0.0.1 --port 8000
```
API docs available at: `http://127.0.0.1:8000/docs`

### 3. Launch the Streamlit UI
```bash
cd frontend
streamlit run main.py
```
Open: `http://localhost:8501`

### 4. Or Call the API Directly
```bash
curl -X POST "http://127.0.0.1:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "batting_team": "CSK",
       "bowling_team": "RCB",
       "venue": "m_chinnaswamy_stadium",
       "runs_to_win": 50,
       "balls_remaining": 30,
       "wickets_remaining": 7,
       "first_inning_total": 180
     }'
```

---

## 🔌 API Reference

### `POST /predict`

**Request Body:**

| Field | Type | Description |
|---|---|---|
| `batting_team` | string | Team code e.g. `"CSK"` |
| `bowling_team` | string | Team code e.g. `"RCB"` |
| `venue` | string | Venue slug e.g. `"m_chinnaswamy_stadium"` |
| `runs_to_win` | int | Runs still needed |
| `balls_remaining` | int | Balls left in innings |
| `wickets_remaining` | int | Wickets in hand |
| `first_inning_total` | int | 1st innings total |

**Response:**

```json
{
  "input_state": { "batting_team": "CSK", "curr_run_rate": 9.6, "..." : "..." },
  "logistic_regression": {
    "batting_team_win": 0.38,
    "bowling_team_win": 0.62,
    "predicted_winner": "RCB"
  },
  "xgboost": { "...": "..." },
  "catboost": { "...": "..." },
  "ensemble": { "...": "..." }
}
```

### `GET /`
Health check — returns `{"status": "ok"}`.

### `GET /about`
Model and version info.

---

## 🏟️ Supported Venues (40 total)

<details>
<summary>Click to expand full venue list</summary>

| Display Name | Slug |
|---|---|
| M Chinnaswamy Stadium | `m_chinnaswamy_stadium` |
| Wankhede Stadium | `wankhede_stadium` |
| Eden Gardens | `eden_gardens` |
| Narendra Modi Stadium | `narendra_modi_stadium` |
| MA Chidambaram Stadium | `ma_chidambaram_stadium` |
| Arun Jaitley Stadium | `arun_jaitley_stadium` |
| Rajiv Gandhi International Stadium | `rajiv_gandhi_international_stadium` |
| Sawai Mansingh Stadium | `sawai_mansingh_stadium` |
| Punjab Cricket Association IS Bindra Stadium | `punjab_cricket_association_is_bindra_stadium` |
| ... (31 more) | — |

</details>

---

## 🏢 Supported Teams (10 active)

| Code | Team |
|---|---|
| CSK | Chennai Super Kings |
| MI | Mumbai Indians |
| RCB | Royal Challengers Bengaluru |
| KKR | Kolkata Knight Riders |
| SRH | Sunrisers Hyderabad |
| DC | Delhi Capitals |
| PBKS | Punjab Kings |
| RR | Rajasthan Royals |
| GT | Gujarat Titans |
| LSG | Lucknow Super Giants |

---

## 🖥️ Deployment

| Component | Platform | Plan |
|---|---|---|
| FastAPI Backend | Render | Free |
| Streamlit Frontend | Streamlit Cloud | Free |
| Python Version | 3.11.9 | — |

### Free Tier Limitations
| Resource | Limit |
|---|---|
| RAM | 512 MB |
| CPU | 0.1 vCPU |
| Comfortable concurrent users | 3–5 |
| Requests/minute | ~20–30 |
| Idle sleep after | 15 minutes |
| Cold start time | 30–60 seconds |

---

## ⚠️ Known Limitations

- **Venue nulls in 2024–25 raw data** — venue was merged from additional source datasets; unknown venues fall back to zero-vector encoding.
- **No probability calibration** — XGBoost and CatBoost probabilities may be overconfident. Platt scaling / isotonic regression is a planned improvement.
- **Player features not used at inference time** — `batting_average`, `career_strike_rate`, `exp_bowler_eco`, `exp_bowler_avg` are trained on but the API does not currently accept per-ball player inputs. Team-level features dominate inference.
- **Retired/defunct teams** — DC Old (Deccan Chargers), KTK, PWI, GL are not supported in the inference UI.
- **Super Overs not handled** — any `inning > 2` rows are dropped during training.

---

## 🛣️ Roadmap

- [ ] Probability calibration (Platt Scaling / Isotonic Regression)
- [ ] Per-ball player stat input at inference
- [ ] Win probability chart across the innings (chart history)
- [ ] Docker deployment
- [ ] Live data ingestion (Cricbuzz / Cricinfo scraper)
- [ ] SHAP feature importance explanations in UI
- [ ] Upgrade to paid hosting to eliminate cold start delays

---

## 🙏 Credits

- Dataset: [dgsports](https://www.kaggle.com/datasets/dgsports/ipl-ball-by-ball-2008-to-2022) and [sahiltailor](https://www.kaggle.com/datasets/sahiltailor/ipl-2024-ball-by-ball-dataset) on Kaggle
- Built with: scikit-learn, XGBoost, CatBoost, FastAPI, Streamlit, Pydantic

---

*For educational and portfolio purposes only. Not affiliated with BCCI or IPL.*
