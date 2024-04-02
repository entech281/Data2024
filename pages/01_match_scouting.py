import config
import streamlit as st
config.configure(st.secrets) #TODO: how to ensure this happens no matter which page you start on?
import time
import controller
import tba
from models import ScoutingRecord, ClimbEnum, PickupEnum, Matches
from gsheet_backend import write_match_scouting_row
from st_scoring_widget import frc_scoring_tracker

FORM_VERSION_KEY = "form_version"

INITIAL_FORM_VERSION = 1
ALL_TEAMS = tba.get_all_pch_team_numbers()


if FORM_VERSION_KEY not in st.session_state:
    st.session_state[FORM_VERSION_KEY] = INITIAL_FORM_VERSION


def notify_saved():
    st.toast(":white_check_mark: Response Saved!")
    time.sleep(2)


def increment_form_version():
    if FORM_VERSION_KEY not in st.session_state:
        st.session_state[FORM_VERSION_KEY] = INITIAL_FORM_VERSION

    old_version = st.session_state[FORM_VERSION_KEY]
    new_version = old_version + 1
    st.session_state[FORM_VERSION_KEY] = new_version


def get_refreshed_form_key(root_name):
    if FORM_VERSION_KEY not in st.session_state:
        st.session_state[FORM_VERSION_KEY] = INITIAL_FORM_VERSION

    # return root_name
    return root_name + str(st.session_state[FORM_VERSION_KEY])


record = ScoutingRecord()

st.title("Match Scouting 2024 DCMP")

match_form = st.form(key="match_row", clear_on_submit=True, border=True)

if "actual_scouter_name" not in st.session_state:
    st.session_state['actual_scouter_name'] = ""

with match_form:
    col1, col2, empty1, empty2 = st.columns(4)
    with col1:
        record.team_number = st.selectbox(label="Team", key="team_number", options=ALL_TEAMS)
        record.match_number = st.selectbox(label="Match", options=Matches.make_matches())

    with col2:
        record.scouter_name = st.text_input("Your Initials (2 chars)", value=st.session_state['actual_scouter_name'],
                                            max_chars=2)
        st.session_state['actual_scouter_name'] = record.scouter_name

        record.team_present = st.checkbox(label="Team Present", key="present",value=True)

    st.header("Auto Scoring")

    record.mobility = st.checkbox("Mobility", key='mobility')
    (record.amp_attempted_auto,
     record.amp_completed_auto,
     record.speaker_subwoofer_attempted_auto,
     record.speaker_subwoofer_completed_auto,
     record.speaker_podium_attempted_auto,
     record.speaker_podium_completed_auto,
     record.speaker_medium_attempted_auto,
     record.speaker_medium_completed_auto
     ) = frc_scoring_tracker(key=get_refreshed_form_key("auto_scoring"))

    st.header("Fouls, Penalties, Problems")
    col1, col2, empty = st.columns(3)

    with col1:
        record.fouls = st.number_input('Foul Counts', key='num_fouls', min_value=0, step=1)

    with col2:
        record.robot_disabled_time = st.number_input('Seconds Disabled', key='robot_disabled_time', min_value=0, step=1)

    st.header("Robot Basics")
    col1, col2, empty = st.columns(3)
    with col1:
        record.robot_pickup = st.radio("Pickup", key="pickup", options=PickupEnum.options(), index=0)
    with col2:
        record.robot_speed = st.slider("Seconds to Cross Whole Field", min_value=3, max_value=10, value=5, step=1,
                                       key="seconds_to_cross")
    with empty:
        pass

    st.header("Teleop Scoring")

    (record.amp_attempted_teleop,
     record.amp_completed_teleop,
     record.speaker_subwoofer_attempted_teleop,
     record.speaker_subwoofer_completed_teleop,
     record.speaker_podium_attempted_teleop,
     record.speaker_podium_completed_teleop,
     record.speaker_medium_attempted_teleop,
     record.speaker_medium_completed_teleop
     ) = frc_scoring_tracker(key=get_refreshed_form_key("telop_scoring"))

    st.header("Defense")
    col1, col2 = st.columns(2)
    with col1:
        record.defense_forced_penalties = st.number_input('Forced Penalties', key='defense_forced_penalties',
                                                          min_value=0, step=1)
    with col2:
        record.defense_rating = st.number_input('Rating', key='defense_rating', min_value=0, step=1, max_value=5)

    st.header("End Game")
    col1, col2, empty1, empty2 = st.columns(4)
    with col1:
        record.rps = st.number_input('RPs', key="rps", min_value=0, max_value=4, step=1)

        record.climb = st.radio("Climb", key='climb', options=ClimbEnum.options(), index=2)
    with col2:
        record.park = st.checkbox("Parked", key='parked')
        record.trap = st.checkbox("Trap", key='trap')

        record.alliance_coop = st.checkbox("Coop", key='coop')

        record.high_note = st.checkbox("HighNote", key='highnote')

    record.strategy = st.text_area("Did they employ a strategy that might exaggerate their stats [Explain]")
    record.notes = st.text_area("Other Comments")

    # note: very important: in streamlit callbacks execute before the rest of the scirpt
    # we need that here to avoid the boundary condition after first form load
    submitted = st.form_submit_button("Submit", type="secondary", disabled=False, use_container_width=False,
                                      on_click=notify_saved)
    if submitted:
        write_match_scouting_row( record)

        increment_form_version()

        st.rerun()
