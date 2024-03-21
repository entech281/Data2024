import pandas as pd
from models import ScoutingRecord
from datetime import datetime

# a local backend that uses a file
LOCAL_DATA_FILE = './data/2024ScoutingData-TestMode.tsv'
#TODO: this is sloppy. need to have this version NOT take sheet as a parameter, and factor the get_match_data code
#TODO int common file
def write_header_if_needed(secrets,sheet):
    pass

def get_match_data(secrets):

    df = pd.read_csv(LOCAL_DATA_FILE,header=0,sep='\t').infer_objects()
    print(df)


    def convert_old_dates(row):
        if 'T' in row['tstamp']:
            return row['tstamp']
        else:
            return datetime.strptime(row['tstamp'],  "%m/%d/%Y %H:%M:%S").isoformat()

    df['pre_parsed_date'] = df.apply(convert_old_dates,axis=1)
    df['tstamp'] = pd.to_datetime(df['pre_parsed_date'])

    return df

def write_scouting_row(secrets, rec:ScoutingRecord):
    rec.calc_fields()
    print("Writing Record:",rec)

