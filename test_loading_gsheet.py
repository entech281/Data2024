from gsheet_backend import get_match_data
import toml
import team_analysis


def get_creds():
    with open('.streamlit/secrets.toml', 'r') as f:
        config = toml.load(f)
    return config['gsheets']

def test_loading_sheet():

    df = get_match_data(get_creds())
    assert 5 == len(df)

def test_analysis():
    df = get_match_data(get_creds())
    (a,s) = team_analysis.analyze(df)
    print(a)
    print (s)