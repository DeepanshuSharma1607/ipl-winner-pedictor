import streamlit as st
import requests


st.set_page_config(
    page_title="IPL Win Predictor",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_URL = "http://127.0.0.1:8000/predict"

VENUES_DISPLAY = [
    "M Chinnaswamy Stadium",
    "Punjab Cricket Association IS Bindra Stadium",
    "Feroz Shah Kotla",
    "Arun Jaitley Stadium",
    "Wankhede Stadium",
    "Eden Gardens",
    "Sawai Mansingh Stadium",
    "Rajiv Gandhi International Stadium",
    "MA Chidambaram Stadium",
    "Dr DY Patil Sports Academy",
    "Newlands",
    "St George's Park",
    "Kingsmead",
    "SuperSport Park",
    "Buffalo Park",
    "New Wanderers Stadium",
    "De Beers Diamond Oval",
    "OUTsurance Oval",
    "Brabourne Stadium",
    "Sardar Patel Stadium",
    "Barabati Stadium",
    "Vidarbha Cricket Association Stadium",
    "Himachal Pradesh Cricket Association Stadium",
    "Nehru Stadium",
    "Holkar Cricket Stadium",
    "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium",
    "Subrata Roy Sahara Stadium",
    "Maharashtra Cricket Association Stadium",
    "Shaheed Veer Narayan Singh International Stadium",
    "JSCA International Stadium Complex",
    "Sheikh Zayed Stadium",
    "Sharjah Cricket Stadium",
    "Dubai International Cricket Stadium",
    "Saurashtra Cricket Association Stadium",
    "Green Park",
    "Narendra Modi Stadium",
    "Zayed Cricket Stadium",
    "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium",
    "Barsapara Cricket Stadium",
    "Maharaja Yadavindra Singh International Cricket Stadium",
]


def venue_to_slug(display_name: str) -> str:
    """Mirrors the notebook's venue normalization."""
    return (
        display_name.split(",")[0]
        .strip()
        .lower()
        .replace(" ", "_")
    )


VENUE_SLUG_MAP = {v: venue_to_slug(v) for v in VENUES_DISPLAY}

TEAMS = {
    "CSK": {"name": "Chennai Super Kings", "color": "#FFCC00", "bg": "#1a1200", "emoji": "🦁"},
    "MI": {"name": "Mumbai Indians", "color": "#005EA6", "bg": "#001529", "emoji": "🔵"},
    "RCB": {"name": "Royal Challengers Bengaluru", "color": "#E03A3E", "bg": "#1a0000", "emoji": "🔴"},
    "KKR": {"name": "Kolkata Knight Riders", "color": "#8A2BE2", "bg": "#0d0019", "emoji": "🟣"},
    "SRH": {"name": "Sunrisers Hyderabad", "color": "#FF6200", "bg": "#1a0d00", "emoji": "🌅"},
    "DC": {"name": "Delhi Capitals", "color": "#0078BC", "bg": "#001829", "emoji": "🔷"},
    "PBKS": {"name": "Punjab Kings", "color": "#CC0000", "bg": "#1a0000", "emoji": "🦁"},
    "RR": {"name": "Rajasthan Royals", "color": "#E91E8C", "bg": "#1a0014", "emoji": "👑"},
    "GT": {"name": "Gujarat Titans", "color": "#1D7EC2", "bg": "#001520", "emoji": "⚡"},
    "LSG": {"name": "Lucknow Super Giants", "color": "#00B2A9", "bg": "#001a19", "emoji": "🔵"},
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Base & Background ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #080c14 !important;
    font-family: 'DM Sans', sans-serif;
    color: #e8eaf0;
}
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 40% at 50% 0%, rgba(0,180,120,0.08) 0%, transparent 70%),
        radial-gradient(ellipse 60% 30% at 20% 100%, rgba(0,100,220,0.06) 0%, transparent 70%),
        #080c14 !important;
}
[data-testid="stHeader"], [data-testid="stToolbar"] { background: transparent !important; }
[data-testid="stSidebar"] { background: #0d1220 !important; }

/* ── Hero header ── */
.hero-header {
    text-align: center;
    padding: 2rem 0 1.5rem;
    position: relative;
}
.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: clamp(3rem, 6vw, 5.5rem);
    letter-spacing: 0.04em;
    background: linear-gradient(135deg, #00e676 0%, #00b4d8 50%, #7c4dff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
    margin: 0;
}
.hero-sub {
    font-size: 0.95rem;
    color: #8892a4;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 0.5rem;
    font-weight: 500;
}
.hero-divider {
    width: 60px; height: 3px;
    background: linear-gradient(90deg, #00e676, #00b4d8);
    border-radius: 2px;
    margin: 1rem auto 0;
}

/* ── Section labels ── */
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #00e676;
    margin-bottom: 0.5rem;
    font-weight: 600;
}

/* ── Glass card ── */
.glass-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.5rem;
    backdrop-filter: blur(12px);
    margin-bottom: 1rem;
}

/* ── Team badge ── */
.team-badge {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 16px;
    border-radius: 12px;
    border: 1.5px solid;
    margin-top: 0.5rem;
    transition: all 0.2s;
}
.team-badge-code {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.8rem;
    letter-spacing: 0.05em;
    line-height: 1;
}
.team-badge-name {
    font-size: 0.78rem;
    color: #8892a4;
    line-height: 1.3;
}

/* ── Stat pills ── */
.stat-row {
    display: flex; gap: 10px; flex-wrap: wrap;
    margin: 1rem 0;
}
.stat-pill {
    flex: 1; min-width: 110px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 12px 14px;
    text-align: center;
}
.stat-pill-val {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.6rem;
    letter-spacing: 0.05em;
    line-height: 1;
}
.stat-pill-label {
    font-size: 0.65rem;
    color: #8892a4;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-top: 4px;
}

/* ── Phase badge ── */
.phase-tag {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* ── Win bar ── */
.win-bar-wrap { margin: 0.6rem 0; }
.win-bar-header {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 5px;
}
.win-bar-team {
    font-size: 0.88rem;
    font-weight: 600;
    color: #e8eaf0;
}
.win-bar-pct {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.92rem;
    font-weight: 600;
}
.win-bar-track {
    background: rgba(255,255,255,0.07);
    border-radius: 6px;
    height: 10px;
    overflow: hidden;
}
.win-bar-fill {
    height: 100%;
    border-radius: 6px;
    transition: width 0.6s cubic-bezier(.4,0,.2,1);
}

/* ── Model card ── */
.model-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.8rem;
    position: relative;
    overflow: hidden;
}
.model-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.model-card.lr::before  { background: linear-gradient(90deg, #7c4dff, #448aff); }
.model-card.xgb::before { background: linear-gradient(90deg, #ff6d00, #ffd600); }
.model-card.cat::before { background: linear-gradient(90deg, #00e5ff, #00b0ff); }
.model-card.ens::before { background: linear-gradient(90deg, #00e676, #00b4d8, #7c4dff); }

.model-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #8892a4;
    margin-bottom: 0.8rem;
}

/* ── Winner banner ── */
.winner-banner {
    text-align: center;
    padding: 1.5rem;
    border-radius: 16px;
    margin: 1rem 0;
    border: 1px solid;
    position: relative;
    overflow: hidden;
}
.winner-banner-label {
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #8892a4;
    font-family: 'JetBrains Mono', monospace;
}
.winner-banner-team {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.5rem;
    letter-spacing: 0.05em;
    line-height: 1;
    margin: 0.3rem 0;
}
.winner-banner-prob {
    font-size: 1rem;
    color: #8892a4;
}

/* ── Error/warning ── */
.warn-box {
    background: rgba(255,100,0,0.1);
    border: 1px solid rgba(255,100,0,0.3);
    border-radius: 10px;
    padding: 10px 16px;
    color: #ffab40;
    font-size: 0.85rem;
    margin: 0.5rem 0;
}

/* ── Streamlit overrides ── */
.stSelectbox > div > div,
.stNumberInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #e8eaf0 !important;
}
.stSelectbox label, .stNumberInput label { color: #8892a4 !important; font-size: 0.82rem !important; }
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #00e676, #00b4d8) !important;
    color: #080c14 !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.4rem !important;
    letter-spacing: 0.1em !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.7rem 2rem !important;
    cursor: pointer !important;
    transition: opacity 0.2s !important;
    box-shadow: 0 4px 24px rgba(0,230,118,0.25) !important;
}
.stButton > button:hover { opacity: 0.85 !important; }
div[data-testid="stColumns"] { gap: 1rem; }
hr { border-color: rgba(255,255,255,0.07) !important; }
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="hero-header">
    <p class="hero-sub">Ball · by · Ball · Intelligence</p>
    <h1 class="hero-title">🏏 IPL Win Predictor</h1>
    <div class="hero-divider"></div>
</div>
""", unsafe_allow_html=True)


def compute_live_stats(runs_to_win, balls_remaining, first_inning_total):
    balls_bowled = 120 - balls_remaining
    team_runs = (first_inning_total + 1) - runs_to_win
    crr = round((team_runs * 6) / balls_bowled, 2) if balls_bowled > 0 else 0.0
    rrr = round((runs_to_win * 6) / balls_remaining, 2) if balls_remaining > 0 else 36.0
    pressure = round(rrr - crr, 2)
    over_number = balls_bowled // 6
    if over_number <= 5:
        phase, phase_label, phase_color = 0, "Powerplay", "#00e676"
    elif over_number <= 14:
        phase, phase_label, phase_color = 1, "Middle Overs", "#ffd600"
    else:
        phase, phase_label, phase_color = 2, "Death Overs", "#ff5252"
    return crr, rrr, pressure, phase_label, phase_color


def win_bar(team, pct, color, is_winner=False):
    bold = "font-weight:700;" if is_winner else ""
    trophy = " 🏆" if is_winner else ""
    return f"""
    <div class="win-bar-wrap">
        <div class="win-bar-header">
            <span class="win-bar-team" style="{bold}color:{'#e8eaf0' if not is_winner else color}">{team}{trophy}</span>
            <span class="win-bar-pct" style="color:{color}">{pct * 100:.1f}%</span>
        </div>
        <div class="win-bar-track">
            <div class="win-bar-fill" style="width:{pct * 100:.1f}%;background:{color};"></div>
        </div>
    </div>
    """


def model_card(cls, label, model_data, bat_team, bowl_team, bat_color, bowl_color):
    bat_win = model_data["batting_team_win"]
    bowl_win = model_data["bowling_team_win"]
    winner = model_data["predicted_winner"]
    is_bat_win = winner == bat_team

    bar_bat = win_bar(bat_team, bat_win, bat_color, is_bat_win)
    bar_bowl = win_bar(bowl_team, bowl_win, bowl_color, not is_bat_win)

    st.markdown(f"""
    <div class="model-card {cls}">
        <div class="model-name">{label}</div>
        {bar_bat}
        {bar_bowl}
    </div>
    """, unsafe_allow_html=True)

col_input, col_result = st.columns([1, 1.2], gap="large")

with col_input:
    st.markdown('<div class="section-label">⚡ Match Setup</div>', unsafe_allow_html=True)

    team_list = list(TEAMS.keys())

    bat_col, bowl_col = st.columns(2)
    with bat_col:
        batting_team = st.selectbox("🏏 Batting Team", team_list, index=0, key="bat")
    with bowl_col:
        default_bowl_idx = 1 if team_list[0] != team_list[1] else 2
        bowling_team = st.selectbox("🎯 Bowling Team", team_list, index=default_bowl_idx, key="bowl")

    # Team badge display
    if batting_team and bowling_team:
        b1 = TEAMS[batting_team]
        b2 = TEAMS[bowling_team]
        badge_col1, vs_col, badge_col2 = st.columns([5, 1, 5])
        with badge_col1:
            st.markdown(f"""
            <div class="team-badge" style="border-color:{b1['color']}22;background:{b1['bg']};">
                <span style="font-size:1.8rem">{b1['emoji']}</span>
                <div>
                    <div class="team-badge-code" style="color:{b1['color']}">{batting_team}</div>
                    <div class="team-badge-name">{b1['name']}</div>
                </div>
            </div>""", unsafe_allow_html=True)
        with vs_col:
            st.markdown(
                "<div style='text-align:center;padding-top:1.2rem;font-family:Bebas Neue,sans-serif;font-size:1.4rem;color:#444;'>VS</div>",
                unsafe_allow_html=True)
        with badge_col2:
            st.markdown(f"""
            <div class="team-badge" style="border-color:{b2['color']}22;background:{b2['bg']};">
                <span style="font-size:1.8rem">{b2['emoji']}</span>
                <div>
                    <div class="team-badge-code" style="color:{b2['color']}">{bowling_team}</div>
                    <div class="team-badge-name">{b2['name']}</div>
                </div>
            </div>""", unsafe_allow_html=True)

    # Same team warning
    if batting_team == bowling_team:
        st.markdown('<div class="warn-box">⚠️ Batting and bowling teams cannot be the same.</div>',
                    unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('<div class="section-label">📍 Venue</div>', unsafe_allow_html=True)
    venue_display = st.selectbox("Select Stadium", VENUES_DISPLAY, index=0, label_visibility="collapsed")
    venue_slug = VENUE_SLUG_MAP[venue_display]
    st.markdown(f"""
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;
         color:#00e676;background:rgba(0,230,118,0.07);
         padding:6px 12px;border-radius:8px;margin-top:4px;
         border:1px solid rgba(0,230,118,0.2);">
        slug → {venue_slug}
    </div>""", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('<div class="section-label">📊 Live Situation</div>', unsafe_allow_html=True)

    sit1, sit2 = st.columns(2)
    with sit1:
        first_inning_total = st.number_input("1st Innings Total", min_value=50, max_value=350, value=180, step=1)
        runs_to_win = st.number_input("Runs to Win", min_value=1, max_value=350, value=50, step=1)
    with sit2:
        balls_remaining = st.number_input("Balls Remaining", min_value=1, max_value=120, value=30, step=1)
        wickets_remaining = st.number_input("Wickets Remaining", min_value=1, max_value=10, value=7, step=1)

    crr, rrr, pressure, phase_label, phase_color = compute_live_stats(
        runs_to_win, balls_remaining, first_inning_total
    )

    pressure_color = "#ff5252" if pressure > 4 else "#ffd600" if pressure > 1 else "#00e676"

    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-pill">
            <div class="stat-pill-val" style="color:#00b4d8">{crr:.2f}</div>
            <div class="stat-pill-label">Curr RR</div>
        </div>
        <div class="stat-pill">
            <div class="stat-pill-val" style="color:#ff6d00">{rrr:.2f}</div>
            <div class="stat-pill-label">Req RR</div>
        </div>
        <div class="stat-pill">
            <div class="stat-pill-val" style="color:{pressure_color}">{pressure:+.2f}</div>
            <div class="stat-pill-label">Pressure</div>
        </div>
        <div class="stat-pill">
            <div class="stat-pill-val">
                <span class="phase-tag" style="background:{phase_color}22;color:{phase_color};
                      border:1px solid {phase_color}44;font-size:0.7rem">{phase_label}</span>
            </div>
            <div class="stat-pill-label">Phase</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)


    can_predict = batting_team != bowling_team
    predict_clicked = st.button("🔮 Predict Win Probability", disabled=not can_predict)

with col_result:
    st.markdown('<div class="section-label">🏆 Win Probability</div>', unsafe_allow_html=True)

    if not predict_clicked:
        st.markdown("""
        <div class="glass-card" style="text-align:center;padding:3rem 2rem;">
            <div style="font-size:4rem;margin-bottom:1rem">🏏</div>
            <div style="font-family:'Bebas Neue',sans-serif;font-size:1.8rem;
                 letter-spacing:0.05em;color:#2a3040;margin-bottom:0.5rem">
                Fill in match details
            </div>
            <div style="color:#4a5568;font-size:0.85rem">
                Configure the match situation on the left and hit<br>
                <strong style="color:#00e676">Predict Win Probability</strong> to see AI-powered analysis
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        if not can_predict:
            st.error("Teams must be different.")
        else:
            payload = {
                "batting_team": batting_team,
                "bowling_team": bowling_team,
                "venue": venue_slug,
                "runs_to_win": int(runs_to_win),
                "balls_remaining": int(balls_remaining),
                "wickets_remaining": int(wickets_remaining),
                "first_inning_total": int(first_inning_total),
            }

            with st.spinner("Consulting three AI oracles… 🔮"):
                try:
                    response = requests.post(API_URL, json=payload, timeout=10)

                    if response.status_code == 200:
                        data = response.json()
                        ens = data["ensemble"]
                        bat_pct = ens["batting_team_win"]
                        bowl_pct = ens["bowling_team_win"]
                        winner = ens["predicted_winner"]

                        bat_color = TEAMS[batting_team]["color"]
                        bowl_color = TEAMS[bowling_team]["color"]
                        win_color = bat_color if winner == batting_team else bowl_color
                        win_team = TEAMS[winner]

                        st.markdown(f"""
                        <div class="winner-banner"
                             style="border-color:{win_color}44;
                                    background:linear-gradient(135deg,{win_color}11,{win_color}06);">
                            <div class="winner-banner-label">Ensemble Prediction · Winner</div>
                            <div class="winner-banner-team" style="color:{win_color}">
                                {win_team['emoji']} {winner}
                            </div>
                            <div class="winner-banner-prob">
                                {win_team['name']} — {max(bat_pct, bowl_pct) * 100:.1f}% win probability
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                        <div class="glass-card">
                            <div class="section-label">Ensemble (XGB 50% · CatBoost 30% · LR 20%)</div>
                            {win_bar(batting_team, bat_pct, bat_color, winner == batting_team)}
                            {win_bar(bowling_team, bowl_pct, bowl_color, winner == bowling_team)}
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown('<div class="section-label" style="margin-top:0.5rem">Individual Models</div>',
                                    unsafe_allow_html=True)

                        model_card("lr", "Logistic Regression", data["logistic_regression"], batting_team, bowling_team,
                                   bat_color, bowl_color)
                        model_card("xgb", "XGBoost", data["xgboost"], batting_team, bowling_team, bat_color, bowl_color)
                        model_card("cat", "CatBoost", data["catboost"], batting_team, bowling_team, bat_color,
                                   bowl_color)
                        model_card("ens", "Ensemble (Final)", data["ensemble"], batting_team, bowling_team, bat_color,
                                   bowl_color)

                        with st.expander("🔬 Full feature state sent to API"):
                            state = data.get("input_state", {})
                            rows = ""
                            labels = {
                                "batting_team": "Batting Team", "bowling_team": "Bowling Team",
                                "venue": "Venue", "runs_to_win": "Runs to Win",
                                "req_run_rate": "Req Run Rate", "curr_run_rate": "Curr Run Rate",
                                "balls_remaining": "Balls Remaining", "wickets_remaining": "Wickets Remaining",
                                "match_phase": "Match Phase", "first_inning_total": "1st Innings Total",
                                "pressure": "Pressure", "batting_team_perf": "Batting Team Perf",
                                "bowling_team_perf": "Bowling Team Perf", "crr_rrr_ratio": "CRR/RRR Ratio",
                            }
                            for k, label in labels.items():
                                val = state.get(k, "—")
                                if isinstance(val, float):
                                    val = f"{val:.4f}"
                                rows += f"<tr><td style='color:#8892a4;padding:4px 10px 4px 0'>{label}</td><td style='font-family:JetBrains Mono,monospace;color:#00e676;padding:4px 0'>{val}</td></tr>"
                            st.markdown(f"""
                            <table style="width:100%;border-collapse:collapse;font-size:0.82rem">
                                {rows}
                            </table>""", unsafe_allow_html=True)

                    else:
                        st.markdown(f'<div class="warn-box">❌ API Error {response.status_code}: {response.text}</div>',
                                    unsafe_allow_html=True)

                except requests.exceptions.ConnectionError:
                    st.markdown("""
                    <div class="warn-box">
                        🔌 <strong>Cannot reach API.</strong> Make sure your FastAPI server is running:<br>
                        <code>uvicorn app:app --host 127.0.0.1 --port 8000</code>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f'<div class="warn-box">⚠️ Unexpected error: {e}</div>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;margin-top:3rem;padding-top:1.5rem;
     border-top:1px solid rgba(255,255,255,0.06);
     color:#2a3040;font-size:0.75rem;letter-spacing:0.08em;">
    IPL Win Predictor · Trained on IPL 2008–2026 · LR · XGBoost · CatBoost
</div>
""", unsafe_allow_html=True)

# Run with:  streamlit run main.py