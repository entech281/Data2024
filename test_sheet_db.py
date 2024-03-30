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



secrets = get_creds()
gs = gsheet_backend._connect(secrets)
wb = gs.worksheet("DCMP_Tags")
df = pd.DataFrame(wb.get_all_records())
#print(df)
df['tag_list'] = df['tags'].str.split(",")
df = df.explode('tag_list')[['team_number','tag_list']]
print(df)
print(df.groupby('tag_list')['team_number'].apply(list))

