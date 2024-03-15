from pydantic import BaseModel
import gspread
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials


#CREDENTIAL_PATH="./google_sheet_creds.json"
SHEET_ID='1JHUOVxvL_UDA3tqxTiwWO095eOxppAWJi7PtDnxnGt8'


class ScoutingRecord(BaseModel):
    tstamp: str = datetime.now().isoformat()
    team_number: int = 0
    match_number: str = ''
    scouter_name: str = ''
    team_present: bool = False
    notes_speaker_auto: int = 0
    notes_amp_auto: int = 0
    speaker_subwoofer_completed_auto: int = 0
    speaker_subwoofer_attempted_auto: int = 0
    speaker_podium_completed_auto: int = 0
    speaker_podium_attempted_auto: int = 0
    speaker_medium_completed_auto: int = 0
    speaker_medium_attempted_auto: int = 0
    speaker_midfield_completed_auto: int = 0
    speaker_midfield_attempted_auto: int = 0
    alliance_coop: bool = False
    robot_disabled_time: int = 0
    robot_speed: float = 0.0
    notes_speaker_teleop: int = 0
    notes_amp_teleop: int = 0
    speaker_subwoofer_completed_teleop: int = 0
    speaker_subwoofer_attempted_teleop: int = 0
    speaker_podium_completed_teleop: int = 0
    speaker_podium_attempted_teleop: int = 0
    speaker_medium_completed_teleop: int = 0
    speaker_medium_attempted_teleop: int = 0
    speaker_midfield_completed_teleop: int = 0
    speaker_midfield_attempted_teleop: int = 0
    park: bool = False
    climb: bool = False
    high_note: bool = False
    trap: bool = False
    penalties: int = 0
    rps: int = 0
    mobility: bool = False
    fouls: int = 0
    defense_rating: int = 0
    defense_forced_penalties: int = 0
    notes: str = ''


    def calc_fields(self):
        self.notes_speaker_teleop = self.speaker_subwoofer_completed_teleop +\
                                    self.speaker_podium_completed_teleop +\
                                    self.speaker_medium_completed_teleop + self.speaker_midfield_completed_teleop
    def as_tuple(self):
        return list(self.model_dump().values())


    @staticmethod
    def dot_column_headers():
        return [ f.replace('_','.') for f in ScoutingRecord.__fields__.keys() ]


def connect_sheet(secrets):


    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
    ]

    credentials = Credentials.from_service_account_info(
        secrets,
        scopes=scopes,
    )
    gs = gspread.authorize(credentials)
    CHARLESTON_TAB = 0
    s = gs.open_by_key(SHEET_ID).get_worksheet(CHARLESTON_TAB)
    return s

def get_match_data(secrets):
    gs = connect_sheet(secrets)
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
    df.columns = ScoutingRecord.dot_column_headers()
    df['tstamp'] = pd.to_datetime(df['tstamp'])
    return df


def write_header_if_needed(secrets,sheet):
    a1 = sheet.cell(1,1)

    if a1.value is None:
        print("Writing Header!",ScoutingRecord.header_columns())
        s = connect_sheet(secrets)
        s.append_row( ScoutingRecord.dot_column_headers())

def write_scouting_row(secrets, rec:ScoutingRecord):
    rec.calc_fields()
    s = connect_sheet(secrets)
    write_header_if_needed(secrets,s)
    t = rec.as_tuple()
    print("Writing Record:",t)
    s.append_row(t)

