import numpy as np

import config
import streamlit as st
config.configure(st.secrets) #TODO: how to ensure this happens no matter which page you start on?
import team_analysis
import controller
import tba
import gsheet_backend

st.set_page_config(layout="wide")
st.title("Scouting Summary")

tag_manager = gsheet_backend.get_tag_manager()
(analyzed, summary) = controller.get_all_joined_team_data()
scouting_summary = summary [ [
    'team_number',
    'scouter.name',
    'robot.weight',
    'robot.width',
    'robot.length',
    'robot.height',
    'under.stage',
    'robot.drive',
    'climb',
    'trap',
    'pref.start',
    'robot.pickup',
    'score.abilities',
    'pref.shoot',
    'autos',
    'strategy',
    'notes'
]]
num_scouted = len(scouting_summary[ scouting_summary['robot.weight'] > 0 ])
total = len(scouting_summary)
scouter_leaderboard = scouting_summary.groupby('scouter.name').count().reset_index()[['scouter.name','team_number']]
scouter_leaderboard.rename(columns={'team_number':'teams'},inplace=True)
scouter_leaderboard = scouter_leaderboard.sort_values(by='teams',ascending=False)
col1, col2,col3 = st.columns(3)
with col1:
    st.metric("Scouted Teams",value=num_scouted)


st.subheader("Scouting Leaderboard")
st.dataframe(scouter_leaderboard, height=400,hide_index=True)

st.subheader("All Data")
st.dataframe(scouting_summary,height=600,hide_index=True)
