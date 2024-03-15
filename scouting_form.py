import streamlit as st

from  models import ScoutingRecord,write_scouting_row,get_match_data
import pandas as pd

record = ScoutingRecord()

st.title("Scouting 2024 Charleston")
match_form = st.form(key="match_row",clear_on_submit=True)

with match_form:
    col1,col2,col3,col4 = st.columns(4)
    with col1:
        record.team_number = st.selectbox(label="Team", options=[281, 2974, 4451, 342, 343])
    with col2:
        record.match_number = st.selectbox(label="Match", options=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])
    with col3:
        record.scouter_name = st.text_input("Scout First Name")
    with col4:
        record.team_present = st.checkbox(label="Present",key="present")

    st.header("Auto")
    record.mobility = st.checkbox("Mobility", key='mobility')

    col1 , col2, col3, col4 = st.columns(4)

    with col1:
        st.text("Subwoofer")
        record.speaker_subwoofer_attempted_auto = st.number_input(':no_entry_sign: Miss',key='speaker_subwoofer_attempted_auto',min_value=0,step=1)
        record.speaker_subwoofer_completed_auto = st.number_input(':white_check_mark: Success',key='speaker_subwoofer_completed_auto',min_value=0,step=1)

    with col2:
        st.text("Podium")
        record.speaker_podium_attempted_auto = st.number_input('Miss',key='speaker_podium_attempted_auto',min_value=0,step=1)
        record.speaker_podium_completed_auto = st.number_input('Success',key='speaker_podium_completed_auto',min_value=0,step=1)

    with col3:
        st.text("Medium")
        record.speaker_medium_attempted_auto = st.number_input('Miss',key='speaker_medium_attempted_auto',min_value=0,step=1)
        record.speaker_medium_completed_auto = st.number_input('Success',key='speaker_medium_completed_auto',min_value=0,step=1)

    with col4:
        st.text("Mid Field")
        record.speaker_midfield_completed_auto = st.number_input('Miss',key='speaker_midfield_completed_auto',min_value=0,step=1)
        record.speaker_midfield_attempted_auto = st.number_input('Success',key='speaker_midfield_attempted_auto',min_value=0,step=1)

    st.header("Fouls, Penalties, Problems")
    col1 ,col2,col3,empty = st.columns(4)

    with col1:
        record.fouls = st.number_input('Foul Counts',key='num_fouls',min_value=0,step=1)
    with col2:
        record.penalties = st.number_input('Penalties',key='num_penalties',min_value=0,step=1)
    with col3:
        record.robot_disabled_time = st.number_input('Seconds Disabled',key='robot_disabled_time',min_value=0,step=1)

    st.header("Teleop ")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.text("Subwoofer")
        record.speaker_subwoofer_attempted_teleop = st.number_input(':no_entry_sign: Miss',key='speaker_subwoofer_attempted_teleop',min_value=0,step=1)
        record.speaker_subwoofer_completed_teleop = st.number_input(':white_check_mark: Success',key='speaker_subwoofer_completed_teleop',min_value=0,step=1)

    with col2:
        st.text("Podium")
        record.speaker_podium_attempted_teleop = st.number_input('Miss',key='speaker_podium_attempted_teleop',min_value=0,step=1)
        record.speaker_podium_completed_teleop = st.number_input('Success',key='speaker_podium_completed_teleop',min_value=0,step=1)

    with col3:
        st.text("Medium")
        record.speaker_medium_attempted_teleop = st.number_input('Miss',key='speaker_medium_attempted_teleop',min_value=0,step=1)
        record.speaker_medium_completed_teleop = st.number_input('Success',key='speaker_medium_completed_teleop',min_value=0,step=1)

    with col4:
        st.text("Mid Field")
        record.speaker_midfield_completed_teleop = st.number_input('Miss',key='speaker_midfield_completed_teleop',min_value=0,step=1)
        record.speaker_midfield_attempted_teleop = st.number_input('Success',key='speaker_midfield_attempted_teleop',min_value=0,step=1)


    st.header("Defense")
    col1 , col2, empty1, empty2 = st.columns(4)
    with col1:
        record.defense_forced_penalties = st.number_input('Forced Penalties',key='defense_forced_penalties',min_value=0,step=1)
    with col2:
        record.defense_rating = st.number_input('Rating',key='defense_rating',min_value=0,step=1)


    st.header("End Game")
    col1, col2,col3,col4,col5= st.columns(5)
    with col1:
        record.rps = st.number_input('RPs', key="rps", min_value=0, max_value=4, step=1)
    with col2:
        record.climb = st.checkbox ("Climbed",key='climb')
    with col3:
        record.park = st.checkbox ("Parked",key='parked')
    with col4:
        record.alliance_coop = st.checkbox ("Coop",key='coop')
    with col5:
        record.high_note = st.checkbox ("HighNote",key='highnote')

    record.notes = st.text_area("Other Comments")

    submitted = st.form_submit_button("Submit", type="secondary", disabled=False, use_container_width=False)
    if submitted:
        write_scouting_row(record)
        st.text("Response Saved!")

st.header("Data")
df = get_match_data(st.secrets["gsheets"])
df['tstamp'] = df['tstamp'].astype(str)
#st.write(df.dtypes)
st.dataframe(df)