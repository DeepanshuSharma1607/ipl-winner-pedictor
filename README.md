# 🏏 IPL Live Win Probability Predictor

A ball-by-ball machine learning model that predicts the **live win probability** of the chasing team during IPL second innings — trained on **278,000+ deliveries** from **IPL 2008 to 2025**.

---

## 📌 Project Overview

This project builds a real-time win probability engine for IPL T20 matches. Given the current match state at any ball during the second innings — runs needed, balls remaining, wickets in hand, current run rate, required run rate, and player quality metrics — the model predicts whether the **batting (chasing) team will win**.

The model was validated live during **CSK vs PBKS, IPL 2026** on April 3, 2026 — predicting a CSK win with **0.89 probability** at over 11.5 when PBKS were 127-3 chasing 210.

---

## 📂 Dataset

| Source | Description |
|--------|-------------|
| `IPL_ball_by_ball_updated.csv` | IPL 2008–2022 ball-by-ball data |
| `deliveries_updated_ipl_upto_2025.csv` | IPL 2024–2025 ball-by-ball data |

- **Combined size:** 278,203 deliveries across 17 seasons
- **Source:** [Kaggle — dgsports/ipl-ball-by-ball-2008-to-2022](https://www.kaggle.com/datasets/dgsports/ipl-ball-by-ball-2008-to-2022)
- Teams standardized for rebrands: Delhi Daredevils → Delhi Capitals, Kings XI Punjab → Punjab Kings, Royal Challengers Bangalore → Royal Challengers Bengaluru

---

## ⚙️ Feature Engineering

All features are computed **ball-by-ball** to simulate a real-time live predictor. Future data leakage is prevented by using **cumsum-then-shift** for all career statistics.

### Match State Features
| Feature | Description |
|---------|-------------|
| `runs_to_win` | Runs still needed to win |
| `balls_remaining` | Legal deliveries left in the innings |
| `wickets_remaining` | Wickets in hand (10 - wickets fallen) |
| `curr_run_rate` | Current run rate at that ball |
| `req_run_rate` | Required run rate to win |
| `crr_rrr_ratio` | CRR / RRR — above 1.0 means batting team is ahead |
| `pressure` | RRR − CRR — positive = under pressure |
| `first_innings_total` | Total set by the first innings |
| `match_phase` | 0 = Powerplay (0–5), 1 = Middle (6–14), 2 = Death (15–19) |

### Player Quality Features (Leak-Free Career Stats)
| Feature | Description |
|---------|-------------|
| `batting_average` | Lagged career batting average (Bayesian smoothed, +50 runs / +2 outs) |
| `career_strike_rate` | Lagged career strike rate (smoothed, +100 runs / +80 balls) |
| `exp_bowler_eco` | Bowler's career economy rate (smoothed, +300 runs / +240 balls) |
| `exp_bowler_avg` | Bowler's career bowling average (smoothed, +300 runs / +10 wickets) |

> **Note:** All career stats are computed as season-by-season aggregates with a one-season lag — ensuring the model never sees future information.

---

## 🧠 Models

### 1. Logistic Regression (Baseline)
- Preprocessing: `OneHotEncoder` for team names + `StandardScaler` for numeric features
- Regularization: `C=0.001` (strong L2)
- Solver: `liblinear`

### 2. XGBoost Classifier
- `n_estimators=200`, `max_depth=3`, `learning_rate=0.05`
- `subsample=0.7`, `colsample_bytree=0.7`
- Regularization: `reg_lambda=5`, `reg_alpha=1`, `gamma=1`
- Dropped high-cardinality columns (`striker`, `non_striker`, `bowler`, `venue`) to reduce overfitting

### 3. Weighted Ensemble
- `0.65 × XGBoost + 0.35 × Logistic Regression`

---

## 📊 Results

### Train / CV / Test Split (Temporal)
| Split | Seasons | Rows |
|-------|---------|------|
| Train | 2008–2021 | ~87,000 |
| CV | 2022–2023 | ~15,000 |
| Test | 2024–2025 | ~15,000 |

> Temporal split is used intentionally — **no random shuffling** — to simulate real-world deployment where the model predicts future seasons from past data.

### Performance Summary

| Model | Split | Accuracy | F1 | AUC |
|-------|-------|----------|----|-----|
| Logistic Regression | Train | 0.7396 | 0.4016 | 0.7818 |
| Logistic Regression | CV | 0.8098 | 0.3465 | 0.7901 |
| Logistic Regression | Test | 0.7339 | 0.3528 | 0.7277 |
| XGBoost | Train | 0.7923 | 0.5524 | 0.8589 |
| XGBoost | CV | 0.8162 | 0.4100 | 0.7763 |
| XGBoost | Test | 0.7460 | 0.4122 | 0.7254 |
| Ensemble (0.65/0.35) | Test | 0.7453 | 0.3947 | 0.7337 |

---

## 🔮 Live Prediction — CSK vs PBKS, IPL 2026

The model was tested **live in production** during a real IPL match on April 3, 2026.

**Match state at over 11.5:**
- PBKS 127-3, chasing 210
- CRR: 10.73 | RRR: 10.16 | Balls remaining: 49 | Wickets remaining: 7

```python
row = pd.DataFrame([{
    'batting_team': 'Punjab Kings',
    'bowling_team': 'Chennai Super Kings',
    'runs_to_win': 83,
    'curr_run_rate': 10.73,
    'req_run_rate': 10.16,
    'crr_rrr_ratio': 1.0561,
    'balls_remaining': 49,
    'wickets_remaining': 7,
    'batting_average': 24.0,
    'career_strike_rate': 125.0,
    'exp_bowler_eco': 12.0,
    'exp_bowler_avg': 27.0,
    'pressure': -0.57,
    'first_innings_total': 209,
    'match_phase': 1
}])
```

**Model output:** CSK win probability = **0.89**
> Despite PBKS being slightly ahead of the required rate, the model correctly identified the difficulty of chasing 210 at Chepauk in the middle overs with a fresh batsman at the crease.

---

## 🚀 How to Run

### 1. Install Dependencies
```bash
pip install numpy pandas scikit-learn xgboost matplotlib seaborn kagglehub
```

### 2. Load Data
```python
import kagglehub
from kagglehub import KaggleDatasetAdapter

df = kagglehub.load_dataset(
    KaggleDatasetAdapter.PANDAS,
    "dgsports/ipl-ball-by-ball-2008-to-2022",
    "IPL_ball_by_ball_updated.csv"
)
```

### 3. Run the Notebook
Open `IPL_Win_Predictor.ipynb` in Jupyter or Google Colab and run all cells top to bottom.

### 4. Make a Live Prediction
```python
row = pd.DataFrame([{
    'batting_team': 'Mumbai Indians',
    'bowling_team': 'Chennai Super Kings',
    'runs_to_win': 48,
    'curr_run_rate': 8.5,
    'req_run_rate': 9.6,
    'crr_rrr_ratio': 0.88,
    'balls_remaining': 30,
    'wickets_remaining': 7,
    'batting_average': 28,
    'career_strike_rate': 140,
    'exp_bowler_eco': 7.2,
    'exp_bowler_avg': 26,
    'pressure': 1.1,
    'first_innings_total': 170,
    'match_phase': 2
}])

pred = xgb_pipe.predict(row)
prob = xgb_pipe.predict_proba(row)
print(f"Win probability: {prob[0][1]:.2%}")
```

---

## 📁 Project Structure

```
ipl-win-predictor/
│
├── IPL_Win_Predictor.ipynb     # Main notebook
├── README.md                   # This file
│
├── data/
│   ├── IPL_ball_by_ball_updated.csv
│   └── deliveries_updated_ipl_upto_2025.csv
│
└── models/
    ├── logistic_regression_pipe.pkl
    └── xgboost_pipe.pkl
```

---

## 🔧 Known Limitations & Future Work

- **Class imbalance:** Batting team wins only ~27% of balls in dataset. Adding `class_weight='balanced'` or SMOTE would improve minority class recall.
- **Venue effect:** 34,000 venue nulls in 2024–25 data meant venue was dropped. Home advantage is significant in IPL and could improve predictions.
- **No hyperparameter tuning:** Manual parameter selection used. Optuna or GridSearchCV could push AUC higher.
- **No probability calibration:** XGBoost probabilities may be overconfident. Platt scaling or isotonic regression calibration is a planned improvement.
- **Player form:** Career stats used instead of rolling form windows (last 10 innings). Short-term form matters in T20.

---

This project is for educational and portfolio purposes. Dataset credit: [dgsports on Kaggle](https://www.kaggle.com/datasets/dgsports/ipl-ball-by-ball-2008-to-2022).
