from gsheet_backend import get_match_data
import toml
import team_analysis
import pandas as pd

def test_that_tests_run():
    pass

def get_creds():
    with open('.streamlit/secrets.toml', 'r') as f:
        config = toml.load(f)
    return config['gsheets']

def test_loading_raw_data():
    df = get_match_data(get_creds())
    (a, s) = team_analysis.analyze(df)
    print(a)
    print(s)

