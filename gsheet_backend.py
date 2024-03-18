from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
from models import ScoutingRecord
from datetime import datetime

SHEET_ID='1JHUOVxvL_UDA3tqxTiwWO095eOxppAWJi7PtDnxnGt8'
def write_header_if_needed(secrets,sheet):

    cell_value = sheet.acell('A1').value
    #print("cell value=*%s*, type=%s" % (cell_value, type(cell_value)) )
    if cell_value is None or len(cell_value) == 0 or cell_value=="None":
        #print("Writing Header!",ScoutingRecord.dot_column_headers())
        s = _connect_sheet(secrets)
        s.append_row( ScoutingRecord.dot_column_headers())

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
    write_header_if_needed(secrets,gs)
    d = gs.get()

    list_of_record=[]
    for r in d[1:]:
        dr = dict(zip(ScoutingRecord.snake_column_headers(),r))
        sr = ScoutingRecord(**dr)
        list_of_record.append(sr)

    #this incantation from SO https://stackoverflow.com/questions/61814887/how-to-convert-a-list-of-pydantic-basemodels-to-pandas-dataframe
    raw_data = [r.model_dump() for r in list_of_record]
    if len(raw_data) > 0:
        df = pd.DataFrame(raw_data)
        df.columns = ScoutingRecord.dot_column_headers()

        def convert_old_dates(row):
            if 'T' in row['tstamp']:
                return row['tstamp']
            else:
                return datetime.strptime(row['tstamp'],  "%m/%d/%Y %H:%M:%S").isoformat()

        df['pre_parsed_date'] = df.apply(convert_old_dates,axis=1)
        df['tstamp'] = pd.to_datetime(df['pre_parsed_date'])
    else:
        df = pd.DataFrame(columns=ScoutingRecord.dot_column_headers())

    return df




def write_scouting_row(secrets, rec:ScoutingRecord):
    rec.calc_fields()
    s = _connect_sheet(secrets)

    t = rec.as_tuple()
    print("Writing Record:",t)
    s.append_row(t)
