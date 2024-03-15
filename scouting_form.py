import streamlit as st

from  models import ScoutingRecord,ClimbEnum,PickupEnum
from gsheet_backend import write_scouting_row,get_match_data
import pandas as pd

def build_scouting_form():
    record = ScoutingRecord()
    SECRETS = st.secrets["gsheets"]
    st.title("Scouting 2024 Charleston")
    match_form = st.form(key="match_row",clear_on_submit=True,border=True)

    if "actual_scouter_name" not in st.session_state:
        st.session_state['actual_scouter_name'] = ""


    with match_form:
        col1,col2,col3,col4 = st.columns(4)
        with col1:
            record.team_number = st.selectbox(label="Team", options=[281, 2974, 4451, 342, 343])
        with col2:
            record.match_number = st.selectbox(label="Match", options=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])
        with col3:
            record.scouter_name = st.text_input("Scout Name",value=st.session_state['actual_scouter_name'])
            st.session_state['actual_scouter_name'] = record.scouter_name
        with col4:
            record.team_present = st.checkbox(label="Present",key="present")

        st.header("Auto")


        col1 , col2, col3, col4,col5 = st.columns(5)
        SUCCESS_LABEL = ':white_check_mark: Success'
        MISS_LABEL = ':no_entry_sign: Miss'

        #TODO: this whole block and the auto block could be done with one function over tuple of (col, label, key)
        with col1:
            st.text("Amp")
            record.notes_amp_auto = st.number_input(':white_check_mark: Success',key='notes_amp_auto',min_value=0,step=1)
            record.mobility = st.checkbox("Mobility", key='mobility')
        with col2:
            st.text("Subwoofer")
            record.speaker_subwoofer_attempted_auto = st.number_input(MISS_LABEL,key='speaker_subwoofer_attempted_auto',min_value=0,step=1)
            record.speaker_subwoofer_completed_auto = st.number_input(SUCCESS_LABEL,key='speaker_subwoofer_completed_auto',min_value=0,step=1)

        with col3:
            st.text("Podium")
            record.speaker_podium_attempted_auto = st.number_input(MISS_LABEL,key='speaker_podium_attempted_auto',min_value=0,step=1)
            record.speaker_podium_completed_auto = st.number_input(SUCCESS_LABEL,key='speaker_podium_completed_auto',min_value=0,step=1)

        with col4:
            st.text("Medium")
            record.speaker_medium_attempted_auto = st.number_input(MISS_LABEL,key='speaker_medium_attempted_auto',min_value=0,step=1)
            record.speaker_medium_completed_auto = st.number_input(SUCCESS_LABEL,key='speaker_medium_completed_auto',min_value=0,step=1)

        with col5:
            st.text("Mid Field")
            record.speaker_midfield_completed_auto = st.number_input(MISS_LABEL,key='speaker_midfield_completed_auto',min_value=0,step=1)
            record.speaker_midfield_attempted_auto = st.number_input(SUCCESS_LABEL,key='speaker_midfield_attempted_auto',min_value=0,step=1)

        st.header("Fouls, Penalties, Problems")
        col1 ,col2,empty = st.columns(3)

        with col1:
            record.fouls = st.number_input('Foul Counts',key='num_fouls',min_value=0,step=1)

        with col2:
            record.robot_disabled_time = st.number_input('Seconds Disabled',key='robot_disabled_time',min_value=0,step=1)

        st.header("Robot Basics")
        col1 ,col2,empty = st.columns(3)
        with col1:
            record.robot_pickup = st.radio("Pickup",key="pickup",options=PickupEnum.options(), index=0)
        with col2:
            record.robot_speed = st.slider("Seconds to Cross Whole Field",min_value=3, max_value=10, value=5, step=1)
        with col3:
            pass
        st.header("Teleop ")

        col1, col2, col3, col4,col5 = st.columns(5)

        with col1:


            st.text("Amp")
            record.notes_amp_teleop = st.number_input(':white_check_mark: Success',key='notes_amp_teleop',min_value=0,step=1)

        with col2:
            st.text("Subwoofer")
            record.speaker_subwoofer_attempted_teleop = st.number_input(MISS_LABEL,key='speaker_subwoofer_attempted_teleop',min_value=0,step=1)
            record.speaker_subwoofer_completed_teleop = st.number_input(':white_check_mark: Success',key='speaker_subwoofer_completed_teleop',min_value=0,step=1)

        with col3:
            st.text("Podium")
            record.speaker_podium_attempted_teleop = st.number_input(MISS_LABEL,key='speaker_podium_attempted_teleop',min_value=0,step=1)
            record.speaker_podium_completed_teleop = st.number_input(SUCCESS_LABEL,key='speaker_podium_completed_teleop',min_value=0,step=1)

        with col4:
            st.text("Medium")
            record.speaker_medium_attempted_teleop = st.number_input(MISS_LABEL,key='speaker_medium_attempted_teleop',min_value=0,step=1)
            record.speaker_medium_completed_teleop = st.number_input(SUCCESS_LABEL,key='speaker_medium_completed_teleop',min_value=0,step=1)

        with col5:
            st.text("Mid Field")
            record.speaker_midfield_completed_teleop = st.number_input(MISS_LABEL,key='speaker_midfield_completed_teleop',min_value=0,step=1)
            record.speaker_midfield_attempted_teleop = st.number_input(SUCCESS_LABEL,key='speaker_midfield_attempted_teleop',min_value=0,step=1)


        st.header("Defense")
        col1 , col2, empty1, empty2 = st.columns(4)
        with col1:
            record.defense_forced_penalties = st.number_input('Forced Penalties',key='defense_forced_penalties',min_value=0,step=1)
        with col2:
            record.defense_rating = st.number_input('Rating',key='defense_rating',min_value=0,step=1, max_value=5)


        st.header("End Game")
        col1, col2,col3,col4,col5= st.columns(5)
        with col1:
            record.rps = st.number_input('RPs', key="rps", min_value=0, max_value=4, step=1)
        with col2:
            record.climb = st.radio ("Climb",key='climb',options=ClimbEnum.options(),index=2)
        with col3:
            record.park = st.checkbox ("Parked",key='parked')
            record.trap = st.checkbox ("Trap",key='trap')
        with col4:
            record.alliance_coop = st.checkbox ("Coop",key='coop')
        with col5:
            record.high_note = st.checkbox ("HighNote",key='highnote')

        record.strategy = st.text_area("Did they employ a strategy that might exaggerate their stats")
        record.notes = st.text_area("Other Comments")

        submitted = st.form_submit_button("Submit", type="secondary", disabled=False, use_container_width=False)
        if submitted:
            write_scouting_row(SECRETS,record)
            st.text("Response Saved!")

    st.header("Data")

    df = get_match_data(SECRETS)
    #df['tstamp'] = df['tstamp'].astype(str)
    st.write(df.dtypes)
    st.dataframe(df)