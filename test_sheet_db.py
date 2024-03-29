import sheet_db
from google.oauth2.service_account import Credentials
import gspread
import toml
import gsheet_backend
import pandas as pd

SHEET_ID='1JHUOVxvL_UDA3tqxTiwWO095eOxppAWJi7PtDnxnGt8'

def get_creds():
    with open('.streamlit/secrets.toml', 'r') as f:
        config = toml.load(f)
    return config['gsheets']


def test_simple_dataframe():
    secrets = get_creds()
    tag_mgr = gsheet_backend.create_team_manager(secrets)

    print("before update tags=",tag_mgr.get_tags_for_team(281))
    tag_mgr.update_tags_for_team(281,['z','y','w'])

    print("after update tags=",tag_mgr.get_tags_for_team(281))

