from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
from models import ScoutingRecord

SHEET_ID='1JHUOVxvL_UDA3tqxTiwWO095eOxppAWJi7PtDnxnGt8'

def _connect_sheet(secrets):
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
    gs = _connect_sheet(secrets)
    d = gs.get()

    rows = d[1:]
    list_of_record=[]
    for r in d[1:]:
        dr = dict(zip(ScoutingRecord.snake_column_headers(),r))
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
        print("Writing Header!",ScoutingRecord.dot_column_headers())
        s = _connect_sheet(secrets)
        s.append_row( ScoutingRecord.dot_column_headers())

def write_scouting_row(secrets, rec:ScoutingRecord):
    rec.calc_fields()
    s = _connect_sheet(secrets)
    write_header_if_needed(secrets,s)
    t = rec.as_tuple()
    print("Writing Record:",t)
    s.append_row(t)
