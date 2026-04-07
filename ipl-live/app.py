from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, computed_field
import joblib
import numpy as np
import pandas as pd

app = FastAPI(
    title="IPL Win Predictor API",
    description="Predicts IPL match win probability using ML models (LR, XGBoost, CatBoost, Ensemble)",
    version="1.0.0"
)


try:
    bundle = joblib.load("ipl_win_predictor.pkl")
    preprocessor  = bundle["preprocessor"]
    lr_model       = bundle["lr_model"]
    xgb_model      = bundle["xgb_model"]
    cat_model      = bundle["cat_model"]
    match_results  = bundle["match_results"]
    match_results  = match_results.sort_values("match_id")
except FileNotFoundError:
    raise RuntimeError("'ipl_win_predictor.pkl' not found. Place it in the same directory as app.py.")


def get_team_perf(team: str, df: pd.DataFrame, role: str = "batting", last_n: int = 10) -> float:
    if role == "batting":
        matches = df[df["batting_team"] == team]
        wins    = matches["bat_won"]
    else:
        matches = df[df["bowling_team"] == team]
        wins    = matches["bowl_won"]

    if len(wins) == 0:
        return 0.5
    return float(wins.tail(last_n).mean())



class IPLMatchState(BaseModel):
    batting_team:      str
    bowling_team:      str
    venue:             str
    runs_to_win:       int
    balls_remaining:   int
    wickets_remaining: int
    first_inning_total: int


    @computed_field
    @property
    def curr_run_rate(self) -> float:
        balls_bowled = 120 - self.balls_remaining
        if balls_bowled <= 0:
            return 0.0
        team_runs = (self.first_inning_total + 1) - self.runs_to_win
        return round((team_runs * 6) / balls_bowled, 4)

    @computed_field
    @property
    def req_run_rate(self) -> float:
        if self.balls_remaining <= 0:
            return 36.0          # effectively impossible — cap at max
        return round((self.runs_to_win * 6) / self.balls_remaining, 4)

    @computed_field
    @property
    def crr_rrr_ratio(self) -> float:
        if self.req_run_rate == 0:
            return 10.0          # already cruising — cap
        ratio = self.curr_run_rate / self.req_run_rate
        return round(float(np.clip(ratio, 0, 10)), 4)

    @computed_field
    @property
    def pressure(self) -> float:
        return round(self.req_run_rate - self.curr_run_rate, 4)

    @computed_field
    @property
    def match_phase(self) -> int:
        # over number from balls already bowled
        over_number = (120 - self.balls_remaining) // 6
        if over_number <= 5:
            return 0    # powerplay
        elif over_number <= 14:
            return 1    # middle overs
        else:
            return 2    # death overs

    @computed_field
    @property
    def batting_team_perf(self) -> float:
        return get_team_perf(self.batting_team, match_results, role="batting")

    @computed_field
    @property
    def bowling_team_perf(self) -> float:
        return get_team_perf(self.bowling_team, match_results, role="bowling")


class WinProbability(BaseModel):
    batting_team:      str
    bowling_team:      str
    batting_team_win:  float
    bowling_team_win:  float
    predicted_winner:  str


class PredictionResponse(BaseModel):
    input_state:         dict
    logistic_regression: WinProbability
    xgboost:             WinProbability
    catboost:            WinProbability
    ensemble:            WinProbability


def build_win_prob(batting_team: str, bowling_team: str, prob: np.ndarray) -> WinProbability:
    bat_win  = round(float(prob[1]), 4)
    bowl_win = round(float(prob[0]), 4)
    winner   = batting_team if bat_win >= 0.5 else bowling_team
    return WinProbability(
        batting_team     = batting_team,
        bowling_team     = bowling_team,
        batting_team_win = bat_win,
        bowling_team_win = bowl_win,
        predicted_winner = winner,
    )


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "IPL Win Predictor API is running."}


@app.get("/about", tags=["Health"])
def about():
    return {
        "title":       "IPL Win Predictor",
        "description": "Ball-by-ball win probability predictor trained on IPL 2008-2023 data.",
        "models":      ["Logistic Regression", "XGBoost", "CatBoost", "Ensemble"],
        "version":     "1.0.0",
    }


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(state: IPLMatchState):
    """
    Predict the win probability for the current match situation.

    **Required inputs:**
    - `batting_team` — e.g. `"CSK"`
    - `bowling_team` — e.g. `"RCB"`
    - `venue` — e.g. `"m_chinnaswamy_stadium"`
    - `runs_to_win` — runs still needed by the chasing team
    - `balls_remaining` — balls left in the innings
    - `wickets_remaining` — wickets in hand for the chasing team
    - `first_inning_total` — total score posted by the first innings team

    All other features (CRR, RRR, pressure, match phase, team performance) are computed automatically.
    """

    feature_cols = [
        "batting_team", "bowling_team", "venue",
        "runs_to_win", "req_run_rate", "balls_remaining",
        "wickets_remaining", "match_phase", "first_inning_total",
        "pressure", "batting_team_perf", "bowling_team_perf",
    ]

    input_dict = {
        "batting_team":      state.batting_team,
        "bowling_team":      state.bowling_team,
        "venue":             state.venue,
        "runs_to_win":       state.runs_to_win,
        "req_run_rate":      state.req_run_rate,
        "balls_remaining":   state.balls_remaining,
        "wickets_remaining": state.wickets_remaining,
        "match_phase":       state.match_phase,
        "first_inning_total": state.first_inning_total,
        "pressure":          state.pressure,
        "batting_team_perf": state.batting_team_perf,
        "bowling_team_perf": state.bowling_team_perf,
    }

    input_df = pd.DataFrame([input_dict]).rename(
        columns={"first_inning_total": "first_innings_total"}
    )

    try:
        input_trans = preprocessor.transform(input_df)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Preprocessing error: {e}")

    lr_prob  = lr_model.predict_proba(input_trans)[0]
    xgb_prob = xgb_model.predict_proba(input_trans)[0]

    cat_df = input_df.copy()
    for col in ["batting_team", "bowling_team", "venue"]:
        cat_df[col] = cat_df[col].astype(str)
    cat_prob = cat_model.predict_proba(cat_df)[0]

    ens_prob = 0.5 * xgb_prob + 0.3 * cat_prob + 0.2 * lr_prob

    bt, bwt = state.batting_team, state.bowling_team
    return PredictionResponse(
        input_state={
            **input_dict,
            "curr_run_rate":  state.curr_run_rate,
            "crr_rrr_ratio":  state.crr_rrr_ratio,
        },
        logistic_regression = build_win_prob(bt, bwt, lr_prob),
        xgboost             = build_win_prob(bt, bwt, xgb_prob),
        catboost            = build_win_prob(bt, bwt, cat_prob),
        ensemble            = build_win_prob(bt, bwt, ens_prob),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

#uvicorn app:app --host 127.0.0.1 --port 8000