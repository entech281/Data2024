from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import numpy as np
import json
from models import ScoutingRecord,PitScoutingRecord
from datetime import datetime
from gspread.utils import ValueRenderOption
from gspread_dataframe import get_as_dataframe,set_with_dataframe

CHARLESTON_MATCH_TAB = 0
CHARLESTON_PIT_TAB = 1
PCH_DCMP_MATCH_TAB = 2
PCH_DCMP_PIT_TAB = 3
#PCH_DCMP_MATCH_TAB = 5
#PCH_DCMP_PIT_TAB = 6


SHEET_ID='1JHUOVxvL_UDA3tqxTiwWO095eOxppAWJi7PtDnxnGt8'

_tag_manager = None

def _connect_sheet(secrets,tab):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
    ]

    credentials = Credentials.from_service_account_info(
        secrets,
        scopes=scopes,
    )
    gs = gspread.authorize(credentials)

    s = gs.open_by_key(SHEET_ID).get_worksheet(tab)
    return s

def _connect(secrets):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
    ]

    credentials = Credentials.from_service_account_info(
        secrets,
        scopes=scopes,
    )
    gs = gspread.authorize(credentials)

    s = gs.open_by_key(SHEET_ID)
    return s

def get_match_data(secrets):
    gs = _connect_sheet(secrets,tab=PCH_DCMP_MATCH_TAB)

    def _write_match_scouting_header_if_needed(secrets, sheet):

        cell_value = sheet.acell('A1').value
        if cell_value is None or len(cell_value) == 0 or cell_value == "None":
            sheet.append_row(ScoutingRecord.dot_column_headers())

    _write_match_scouting_header_if_needed(secrets,gs)

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

def _write_pit_scouting_header_if_needed(secrets, sheet):
    cell_value = sheet.acell('A1').value
    if cell_value is None or len(cell_value) == 0 or cell_value == "None":
        headers=PitScoutingRecord.dot_column_headers()
        print("writing headers",headers)
        sheet.append_row(headers)

def get_tag_manager(secrets):
    global _tag_manager
    if _tag_manager is None:
        gs = _connect(secrets)
        tag_tab = gs.worksheet("TEST_TAGS")
        _tag_manager =  TeamTagManager(tag_tab)
    return _tag_manager


class TeamTagManager:
    def __init__(self, worksheet_tab):
        print("Initialzing TagManager")
        self.worksheet_tab = worksheet_tab
        self.fetch()

    def update(self):
        print("Refreshing Team Tags!",self.df)

        set_with_dataframe(self.worksheet_tab, self.df)
        self.fetch()

    def fetch(self):
        df =  get_as_dataframe(self.worksheet_tab, usecols=[0, 1]).dropna(how='all')
        df = df.replace(np.NaN, '')
        print("Fetched Value=",df)
        self.df = df

    def get_tags_for_team(self,team_number):
        t = self.df[ self.df["team_number"] == team_number]
        print(t)
        if len(t) != 0:
            s = t.iloc[0]['tags']
            if s is not None and len(s) > 0:
                return s.split(',')
        return []

    def update_tags_for_team(self,team_number, tags):
        print("Update team = ",team_number, "tags=",str(tags))
        tags_str = ",".join(tags)

        if len(self.df[self.df['team_number'] == team_number]) == 0:
            new_tags = pd.DataFrame([ { 'team_number': team_number, 'tags': tags_str }])
            self.df = pd.concat([self.df,new_tags])
        else:
            self.df.loc[self.df['team_number'] == team_number, 'tags'] = tags_str

        print(self.df)

        #set_with_dataframe(self.worksheet_tab, self.df)
        #self.refresh()


def get_pits_data(secrets):
    gs = _connect_sheet(secrets,tab=PCH_DCMP_PIT_TAB)
    _write_pit_scouting_header_if_needed(secrets, gs)

    d = gs.get()
    print("pit data, got", len(d))
    if len(d) == 0:

        return None

    list_of_record = []
    for r in d[1:]:
        dr = dict(zip(PitScoutingRecord.snake_column_headers(), r))
        sr = PitScoutingRecord(**dr)
        list_of_record.append(sr)

    # this incantation from SO https://stackoverflow.com/questions/61814887/how-to-convert-a-list-of-pydantic-basemodels-to-pandas-dataframe
    raw_data = [r.model_dump() for r in list_of_record]
    if len(raw_data) > 0:
        df = pd.DataFrame(raw_data)
        df.columns = PitScoutingRecord.dot_column_headers()

        df['tstamp'] = pd.to_datetime(df['tstamp'])
    else:
        df = pd.DataFrame(columns=PitScoutingRecord.dot_column_headers())
    #print("returning pit data",df)
    return df




def write_match_scouting_row(secrets, rec:ScoutingRecord):
    rec.calc_fields()
    s = _connect_sheet(secrets,tab=PCH_DCMP_MATCH_TAB)
    t = rec.as_tuple()
    print("Writing Record:",t)
    s.append_row(t)

def write_pit_scouting_row(secrets, rec:PitScoutingRecord):
    rec.calc_fields()
    s = _connect_sheet(secrets,tab=PCH_DCMP_PIT_TAB)
    _write_pit_scouting_header_if_needed(secrets,s)
    t = rec.as_tuple()
    print("Writing Record:",t)
    s.append_row(t)
