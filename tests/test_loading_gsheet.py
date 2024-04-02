import gsheet_backend
from gsheet_backend import get_match_data,get_pits_data
import toml
import tba
import team_analysis


def get_creds():
    with open('../.streamlit/secrets.toml', 'r') as f:
        config = toml.load(f)
    return config

def test_loading_pit_data():
    secrets = get_creds()
    print ( get_pits_data(secrets["gsheets"]) )

def test_loading_tag_data():
    secrets = get_creds()
    tag_data = gsheet_backend.get_tag_manager(secrets["gsheets"]).get_tags_by_team()
    print(tag_data)


def test_loading_mega_data():
    secrets = get_creds()
    tba.configure(secrets["tba"]["auth_key"])
    all_data = team_analysis.get_all_joined_team_data(secrets["gsheets"])
    print("Rows = ",len(all_data))
    print(all_data.columns)

def test_pch_team_numbers():
    secrets = get_creds()
    tba.configure(secrets["tba"]["auth_key"])
    print ( tba.get_all_pch_team_numbers())