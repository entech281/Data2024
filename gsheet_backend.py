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
        #print("writing headers",headers)
        sheet.append_row(headers)

def get_tag_manager(secrets):
    global _tag_manager
    if _tag_manager is None:
        gs = _connect(secrets)
        _tag_manager =  TeamTagManager(gs)
    return _tag_manager


class TeamTagManager:
    def __init__(self, gs):
        #print("Initialzing TagManager")
        self.spreadsheet = gs
        self.worksheet_tab = gs.worksheet("DCMP_Tags")
        self.tag_list_sheet = gs.worksheet("TeamTags")
        self.fetch()
        self._load_defined_tags()

    def _load_defined_tags(self):
        tag_list_df = get_as_dataframe(self.tag_list_sheet,usecols=[0]).dropna(how='all')
        self.all_tag_list = list(tag_list_df['Tags'])

    def update(self):
        #print("Refreshing Team Tags!",self.df)

        set_with_dataframe(self.worksheet_tab, self.df)
        self.fetch()

    def fetch(self):
        tag_list_df =  get_as_dataframe(self.worksheet_tab, usecols=[0, 1]).dropna(how='all')
        tag_list_df = tag_list_df.replace(np.NaN, '')
        #print("Fetched Value=",tag_list_df)
        self.df = tag_list_df
        self.df['team_number'] = self.df['team_number'].apply(int)
        tag_list_df['tag_list'] = tag_list_df['tags'].str.split(",")
        tag_list_df = tag_list_df.explode('tag_list')[['team_number', 'tag_list']]

        self.tag_summary = tag_list_df.groupby('tag_list')['team_number'].apply(list)
        #print("TagThing", self.tag_summary)


    def get_tags_by_team(self):
        return self.df [ ['team_number','tag_list']]

    def get_tags_for_team(self,team_number):
        t = self.df[ self.df["team_number"] == team_number]
        #print(t)
        if len(t) != 0:
            s = t.iloc[0]['tags']
            if s is not None and len(s) > 0:
                return s.split(',')
        return []

    def update_tags_for_team(self,team_number, tags):
        #print("Update team = ",team_number, "tags=",str(tags))
        tags_str = ",".join(tags)

        if len(self.df[self.df['team_number'] == team_number]) == 0:
            new_tags = pd.DataFrame([ { 'team_number': team_number, 'tags': tags_str }])
            self.df = pd.concat([self.df,new_tags])
        else:
            self.df.loc[self.df['team_number'] == team_number, 'tags'] = tags_str

        df_to_write = self.df [ ['team_number','tags']]
        set_with_dataframe(self.worksheet_tab, df_to_write)
        self.update()


def get_pits_data(secrets):
    gs = _connect_sheet(secrets,tab=PCH_DCMP_PIT_TAB)
    _write_pit_scouting_header_if_needed(secrets, gs)

    d = gs.get()
    #print("pit data, got", len(d))
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
    # filter to most recent pit scouting row, in caes we have more than one
    most_recent_row_per_team = df[df.groupby('team.number')['tstamp'].transform('max') == df['tstamp']]
    most_recent_row_per_team['team_number'] = most_recent_row_per_team['team.number']
    return most_recent_row_per_team




def write_match_scouting_row(secrets, rec:ScoutingRecord):
    rec.calc_fields()
    s = _connect_sheet(secrets,tab=PCH_DCMP_MATCH_TAB)
    t = rec.as_tuple()
    #print("Writing Record:",t)
    s.append_row(t)

def write_pit_scouting_row(secrets, rec:PitScoutingRecord):
    rec.calc_fields()
    s = _connect_sheet(secrets,tab=PCH_DCMP_PIT_TAB)
    _write_pit_scouting_header_if_needed(secrets,s)
    t = rec.as_tuple()
    #print("Writing Record:",t)
    s.append_row(t)
