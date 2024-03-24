import streamlit as st

import st_scoring_widget
from pch_teams import ALL_TEAMS

from  models import PitScoutingRecord,DriveEnum,PickupEnum,CanClimbEnum, StartLocEnum,PickupEnum,ShotLocEnum
from gsheet_backend import write_pit_scouting_row,get_pits_data

from st_scoring_widget import frc_scoring_tracker
import pandas as pd

FORM_SUBMIT_KEY="pit_form_key"

if FORM_SUBMIT_KEY not in st.session_state:
    st.session_state[FORM_SUBMIT_KEY] = 0

def get_refreshed_form_key(root_name):
    if FORM_SUBMIT_KEY not in st.session_state:
        st.session_state[FORM_SUBMIT_KEY] = 0

    return root_name + str(st.session_state[FORM_SUBMIT_KEY])

def toggle_form_key():
    if FORM_SUBMIT_KEY not in st.session_state:
        st.session_state[FORM_SUBMIT_KEY] = 0

    if st.session_state[FORM_SUBMIT_KEY] == 1:
        st.session_state[FORM_SUBMIT_KEY] = 0
    else:
        st.session_state[FORM_SUBMIT_KEY] = 1

def build_pit_scouting_form():
    record = PitScoutingRecord()
    SECRETS = st.secrets["gsheets"]
    st.title("Pit Scouting 2024 DCMP")

    if "actual_scouter_name" not in st.session_state:
        st.session_state['actual_scouter_name'] = ""

    pit_form = st.form(key="pit_row", clear_on_submit=True, border=True)
    with pit_form:
        col1,col2 = st.columns(2)
        with col1:
            record.team_number = st.selectbox(label="Team", key="team_pit_number", options=ALL_TEAMS)
        with col2:
            record.scouter_name = st.text_input("Your Initials (2 chars)",value=st.session_state['actual_scouter_name'],max_chars=2)
            st.session_state['actual_scouter_name'] = record.scouter_name

        st.header("Robot Specs")

        col1,col2,col3 = st.columns(3)

        with col1:
            record.robot_length = st.number_input(label="Robot Length (in.)", min_value=0.0, max_value=40.0,value=0.0,key="robot_length")
            record.robot_width = st.number_input(label="Robot Width (in.)", min_value=0.0, max_value=40.0,value=0.0,key="robot_width")
            record.robot_height = st.number_input(label="Robot Starting Height (in.)", min_value=0.0, max_value=60.0, value=0.0,key="robot_height")

        with col2:
            record.robot_weight = st.number_input(label="Robot Weight (lbs.)",min_value=0.0, max_value=125.0,value=0.0,key="robot_weight")
            record.robot_drive = st.radio(label = "Drive Train", options=DriveEnum.options(),index=0,key="robot_drive")


        with col3:
            record.under_stage = st.checkbox(label="Can they go under the stage", key="robot_can_stage")
            record.trap = st.checkbox(label = "Trap",key="robot_can_trap")
            record.climb = st.radio(label = "Climb", options=CanClimbEnum.options(),index=2,key="robot_can_climb")

        st.header("Match Interests")
        st.subheader("Choose all that apply")

        col1,col2 = st.columns(2)

        with col1:
            record.pref_start = st.multiselect("Preferred Starting Locations", key="pref_starts", max_selections=3, options=StartLocEnum.options())

            record.robot_pickup = st.radio("Preferred Pickup Locations", key="robot_pickup", index=0,options=PickupEnum.options())

        with col2:
            record.score_abilities = st.multiselect("Scoring Abilities", key="robot_scoring_abilities", max_selections=5, options=ShotLocEnum.options())

            record.pref_shoot = st.multiselect("Preferred Scoring Locations", key="pref_shots", max_selections=5, options=ShotLocEnum.options())

        record.autos = st.text_area("Autonomous'")

        record.notes = st.text_area("Other Comments")

        #note: very important: in streamlit callbacks execute before the rest of the scirpt
        #we need that here to avoid the boundary condition after first form load

        submitted = st.form_submit_button("Submit", type="secondary", disabled=False, use_container_width=False,on_click=toggle_form_key)

        if submitted:
            write_pit_scouting_row(SECRETS,record)
            st.text("Response Saved!");


