
import streamlit as st
import gspread
from dataclasses import dataclass
import pandas as pd
from pydantic import BaseModel
CREDENTIAL_PATH="./google_sheet_creds.json"
SHEET_ID='1JHUOVxvL_UDA3tqxTiwWO095eOxppAWJi7PtDnxnGt8'


class ScoutingRecord(BaseModel):
    team_number: int = 0
    match_number: str = ''
    scouter_name: str = 'Unknown'
    speaker_subwoofer_completed_teleop: int = 0
    speaker_subwoofer_missed_teleop: int = 0
    rps: int = 0
    notes: str = ''

    @staticmethod
    def header_columns():
        #this generates the fields in dot format
        return [ f.replace('_','.') for f in ScoutingRecord.__fields__.keys() ]

record = ScoutingRecord()

def connect_sheet():
    gs = gspread.service_account(CREDENTIAL_PATH)
    CHARLESTON_TAB = 0
    s = gs.open_by_key(SHEET_ID).get_worksheet(CHARLESTON_TAB)
    return s

def get_all_data():
    gs = connect_sheet()
    d = gs.get()

    columns_with_underscores = [ c.replace('.','_') for c in d[0]]
    rows = d[1:]
    list_of_record=[]
    for r in d[1:]:
        dr = dict(zip(columns_with_underscores,r))
        sr = ScoutingRecord(**dr)
        list_of_record.append(sr)

    #this incantation from SO https://stackoverflow.com/questions/61814887/how-to-convert-a-list-of-pydantic-basemodels-to-pandas-dataframe
    df = pd.DataFrame([r.model_dump() for r in list_of_record])
    return df

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

st.header("DATA")
d = get_all_data()
st.write(get_all_data().dtypes )
st.write(get_all_data() )

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

