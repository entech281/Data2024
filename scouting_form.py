import dataclasses as dataclasses
import streamlit as st
import gspread
from dataclasses import dataclass


CREDENTIAL_PATH="./google_sheet_creds.json"
SHEET_ID='1JHUOVxvL_UDA3tqxTiwWO095eOxppAWJi7PtDnxnGt8'
@dataclass
class ScoutingRecord:
    team_number: int
    match_number: str
    scouter_name: str
    speaker_subwoofer_completed_teleop: int
    speaker_subwoofer_missed_teleop: int
    rps: int
    notes: str

    @staticmethod
    def blank_record():
        return ScoutingRecord(0, 0, None, 0, 0, 0, None)

    @staticmethod
    def header_columns():
        return [ f.name.replace('_','.') for f in dataclasses.fields(ScoutingRecord) ]


SHEET_FIELDS=[
    'team.number',
    'match.number',
    'scouter.name',
    #'team.present',
    #'notes.speaker.auto',
    #'notes.amp.auto',
    #'speaker.subwoofer.completed.auto',
    #'speaker.subwoofer.attempted.auto',
    #'speaker.podium.completed.auto',
    #'speaker.podium.attempted.auto',
    #'speaker.medium.completed.auto',
    #'speaker.medium.attempted.auto',
    #'speaker.midfield.completed.auto',
    #'speaker.midfield.attempted.auto',
    #'alliance.coop',
    #'robot.disabled.time',
    #'robot.speed',
    #'notes.speaker.teleop',
    #'notes.amp.teleop',
    'speaker.subwoofer.completed.teleop',
    'speaker.subwoofer.attempted.teleop',
    #'speaker.podium.completed.teleop',
    #'speaker.podium.attempted.teleop',
    #'speaker.medium.completed.teleop',
    #'speaker.medium.attempted.teleop',
    #'speaker.midfield.completed.teleop',
    #'speaker.midfield.attempted.teleop',
    #'park',
    #'climb',
    #'high.note',
    'rps',
    #'mobility',
    #'fouls',
    #'defense.rating',
    #'defense.forced.penalties',
    'notes',
]
record = ScoutingRecord.blank_record()

def connect_sheet():
    gs = gspread.service_account(CREDENTIAL_PATH)
    CHARLESTON_TAB = 0
    s = gs.open_by_key(SHEET_ID).get_worksheet(CHARLESTON_TAB)
    return s

def write_header_if_needed(sheet):
    a1 = sheet.cell(1,1)
    if a1.value is None:
        print("Writing Header!")
        s = connect_sheet()
        s.append_row( ScoutingRecord.header_columns())

def write_scouting_row(rec:ScoutingRecord):
    s = connect_sheet()
    s.append_row(dataclasses.astuple(rec))

write_header_if_needed(connect_sheet())

st.title("Scouting 2024 Charleston")
match_form = st.form(key="match_row",clear_on_submit=True)

with match_form:
    col1,col2,col3 = st.columns(3)
    with col1:
        record.team_number = st.selectbox(label="Team", options=['281', '2974', '4451', '342', '343'])
    with col2:
        record.match_number = st.selectbox(label="Match", options=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])
    with col3:
        record.scouter_name = st.text_input("Scout First Name")

    st.header("Fouls and Penalties")
    col1 ,col2,col3,col4 = st.columns(4)

    with col1:
        num_fouls = st.number_input('Foul Counts',key='num_fouls',min_value=0,step=1)
    with col2:
        num_penalties = st.number_input('Penalties',key='num_penalties',min_value=0,step=1)


    st.header("Scoring")
    col1 ,col2,col3,col4 = st.columns(4)
    with col1:
        st.text("Amp")
        amp_misses = st.number_input(':no_entry_sign: Miss',key='amp_misses',min_value=0,step=1)
        amp_scores = st.number_input(':white_check_mark: Success',key='amp_scores',min_value=0,step=1)


    with col2:
        st.text("Close Speaker")
        record.speaker_subwoofer_missed_teleop = st.number_input('Miss',key='close_speaker_misses',min_value=0,step=1)
        record.speaker_subwoofer_completed_teleop = st.number_input('Success',key='close_speaker_scores',min_value=0,step=1)

    with col3:
        st.text("Podium")
        podium_misses = st.number_input('Miss',key='podium_misses',min_value=0,step=1)
        podium_scores = st.number_input('Success',key='podium_scores',min_value=0,step=1)

    with col4:
        st.text("Far Field")
        far_speaker_misses = st.number_input('Miss',key='far_speaker_misses',min_value=0,step=1)
        far_speaker_scores = st.number_input('Success',key='far_speaker_scores',min_value=0,step=1)

    st.header("End Game")
    col1, col2,col3= st.columns(3)
    with col1:
        record.rps = st.number_input('RPs', key="rps", min_value=0, max_value=4, step=1)
    with col2:
        climbed = st.checkbox ("Climbed",key='disabled_broken')

    with col3:
        parked_broken = st.checkbox ("Parked",key='parked_broken')

    record.notes = st.text_area("Other Notes")

    submitted = st.form_submit_button("Submit", type="secondary", disabled=False, use_container_width=False)
    if submitted:
        write_scouting_row(record)
        st.text("Response Saved!")

