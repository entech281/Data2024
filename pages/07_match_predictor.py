import streamlit as st
import team_analysis
import tba
import gsheet_backend
import pandas as pd

from matplotlib.colors import LinearSegmentedColormap
SECRETS = st.secrets["gsheets"]

TBA_EVENT_KEY = '2024sccha'
CACHE_SECONDS = 60
tba.set_auth_key(st.secrets["tba"]["auth_key"])

@st.cache_data(ttl=CACHE_SECONDS)
def load_match_data():
    raw_data = gsheet_backend.get_match_data(SECRETS)
    return team_analysis.analyze(raw_data)

st.title("Match Preditor")

(analyzed, summary) = load_match_data()
teamlist = tba.get_all_pch_team_numbers()


if len(analyzed) == 0:
    st.header("No Data")
    st.stop()

red_col, blue_col = st.columns(2)



with red_col:
    st.header("Red Team")
    red_teams = st.multiselect("Red Team", key="redteams", max_selections=3, options=teamlist)

with blue_col:
    st.header("Blue Team")
    blue_teams = st.multiselect("Blue Team", key="blueteams", max_selections=3, options=teamlist)

if len(red_teams) == 3 and len(blue_teams) == 3:
    blue_score = pd.DataFrame({'score': summary[summary["team.number"].isin(blue_teams)].sum(numeric_only=True)[
        ['avg_auto', 'avg_teleop', 'avg_notes_speaker', 'avg_notes_amp', 'avg_total_pts', 'epa']
    ]})

    red_score = pd.DataFrame({'score': summary[summary["team.number"].isin(red_teams)].sum(numeric_only=True)[
        ['avg_auto', 'avg_teleop', 'avg_notes_speaker', 'avg_notes_amp', 'avg_total_pts', 'epa']
    ]})
    with red_col:
        st.dataframe(data=red_score, column_config={
            'score': st.column_config.NumberColumn(width='medium', format='%0.2f')
        })
    with blue_col:
        st.dataframe(data=blue_score, column_config={
            'score': st.column_config.NumberColumn(width='medium', format='%0.2f')
        })