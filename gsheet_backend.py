from google.oauth2.service_account import Credentials
from config import current_config
import gspread
import pandas as pd
import numpy as np
from models import ScoutingRecord, PitScoutingRecord
from datetime import datetime
from gspread_dataframe import get_as_dataframe, set_with_dataframe

"""
read data from google sheets. 
MUST return data frames, for compatibility
with df_cache
should NOT have business logic
"""

gsheet_creds = current_config("gsheets")
SHEET_ID = gsheet_creds['sheet_id']

PCH_DCMP_MATCH_TAB = "DCMP Matches"
PCH_DCMP_PIT_TAB = "DCMP Pits"


def _connect_sheet( tab:str):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
    ]

    credentials = Credentials.from_service_account_info(
        gsheet_creds,
        scopes=scopes,
    )
    gs = gspread.authorize(credentials)

    return gs.open_by_key(SHEET_ID).worksheet(tab)


def read_data_on_tab(tab_name:str) -> pd.DataFrame:
    sheet = _connect_sheet(tab_name)
    return get_as_dataframe(sheet)


def write_data_on_tab(df: pd.DataFrame, tab_name:str) -> None:
    sheet = _connect_sheet(tab_name)
    set_with_dataframe(sheet,df)


def append_row(tab_name:str, row_data:dict) -> None:
    sheet = _connect_sheet(tab_name)

    def _write_header_if_needed( sheet):
        cell_value = sheet.acell('A1').value
        if cell_value is None or len(cell_value) == 0 or cell_value == "None":
            sheet.append_row(row_data.keys())

    _write_header_if_needed(sheet)

    sheet.append_row(row_data.values())


