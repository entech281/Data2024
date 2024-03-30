import requests
import pandas as pd
import json
from pprint import pprint
import cachetools.func


auth_key="SET YOUR AUTH KEY"

def get_auth_key():
    return auth_key

def set_auth_key(new_auth_key):
    global auth_key
    auth_key = new_auth_key

class PchEvents:
    DCMP = '2024gacmp'
    CHARLESTON = '2024sccha'
    ANDERSON = '2024scand'
    GWINETT = '2024gagwi'
    DALTON = '2024gadal'
    CARROLTON = '2024gacar'
    ALBANY = '2024gaalb'

class Keys:
    PCH_DISTRICT = '2024pch'
    TEAM_281='frc281'

def _get(url,result_type='json'):
    TBA_API_ROOT = 'https://www.thebluealliance.com/api/v3/'

    response = requests.get(TBA_API_ROOT + url, headers={
        'X-TBA-Auth-Key': get_auth_key()
    })
    if result_type == 'json':
        return response.json()
    else:
        return response.text

def team_number_from_key(frc_team_key):
    return int(frc_team_key.replace('frc',''))

def get_event_rankings(event_key):
    r = _get("/event/{event_key}/rankings".format(event_key=event_key))
    df = pd.DataFrame(r['rankings'])
    df['record'] = df['record'].apply( lambda x: "{0}-{1}-{2}".format(x['wins'],x['losses'],x['ties']) )
    df['team_number'] = df['team_key'].apply(lambda x: team_number_from_key(x))
    return df[ ['team_number','rank','record']]

def get_event_oprs(event_key):
    r = _get("/event/{event_key}/oprs".format(event_key=event_key),result_type='text')
    df = pd.read_json(r,orient='columns').reset_index()
    df['team_number'] = df['index'].apply(team_number_from_key)
    df = df[['team_number','oprs','dprs','ccwms']]
    df.columns = ['team_number','opr','dpr','ccwm']
    return df

@cachetools.func.ttl_cache(maxsize=128, ttl=60*10)
def get_all_pch_team_numbers():
    # use the list of PCH teams
    r = _get("/district/{district_key}/rankings".format(district_key=Keys.PCH_DISTRICT))
    df = pd.DataFrame(r)
    df['team_number'] = df['team_key'].apply(team_number_from_key)
    return list(df['team_number'])
    #print(df)


# not documented, but it is in seconds
@cachetools.func.ttl_cache(maxsize=128, ttl=30)
def get_tba_team_stats(event_name):
    oprs = get_event_oprs('2024sccha')
    ranks = get_event_rankings('2024sccha')
    return pd.merge(ranks,oprs,on='team_number',how='left')

def get_tba_team_stats_for_team(event_name, team_number):
    df = get_tba_team_stats("2024sccha")
    r = df[ df [ 'team_number'] == team_number ].to_dict(orient='records')
    if len(r) > 0:
        d = r[0]
        return {
            'team_number': team_number,
            'opr': '{0:0.1f}'.format(d["opr"]),
            'rank': str(d["rank"]),
            'dpr': '{0:0.1f}'.format(d["dpr"])
        }
    else:
        return {
            'team_number': team_number,
            'opr': 'N/A',
            'rank': 'N/A',
            'dpr': 'N/A'
        }
    return r


