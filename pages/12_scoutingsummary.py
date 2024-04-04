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
scouted_teams = set(scouting_summary[ scouting_summary['robot.weight'] > 0 ]['team_number'].unique())
all_teams =set(tba.get_tba_teams_for_event(tba.PchEvents.DCMP)['team_number'])
#print("all teams:",all_teams)
#print("teams scouted:",scouted_teams)
scouter_leaderboard = scouting_summary.groupby('scouter.name').count().reset_index()[['scouter.name','team_number']]
scouter_leaderboard.rename(columns={'team_number':'teams'},inplace=True)
scouter_leaderboard = scouter_leaderboard.sort_values(by='teams',ascending=False)
col1, col2,col3 = st.columns(3)
with col1:
    st.metric("Scouted Teams",value=len(scouted_teams))
with col2:
    st.metric("Total Teams", value=len(all_teams))



teams_left = all_teams- scouted_teams
st.subheader("Teams we still need to scout")
st.write(teams_left)
st.subheader("Scouting Leaderboard")
st.dataframe(scouter_leaderboard, height=400,hide_index=True)

st.subheader("All Data")
st.dataframe(scouting_summary,height=600,hide_index=True)
