import requests
import pandas as pd
from config import current_config
import cachetools.func


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
    TEAM_281 = 'frc281'


def _get(url, result_type='json'):
    TBA_API_ROOT = 'https://www.thebluealliance.com/api/v3/'

    response = requests.get(TBA_API_ROOT + url, headers={
        'X-TBA-Auth-Key': current_config['tba']['auth_key']
    })
    if result_type == 'json':
        return response.json()
    else:
        return response.text


def team_number_from_key(frc_team_key):
    return int(frc_team_key.replace('frc', ''))

def zero_if_column_missing(df,col_name):
    df_return = df
    if col_name not in df.columns:
        df_return[col_name] = 0
    return df_return

def get_event_rankings(event_key):
    r = _get("/event/{event_key}/rankings".format(event_key=event_key))
    df = pd.DataFrame(r['rankings'])

    if 'record' in df.columns:
        df['record'] = df['record'].apply(lambda x: "{0}-{1}-{2}".format(x['wins'], x['losses'], x['ties']))
        df['team_number'] = df['team_key'].apply(lambda x: team_number_from_key(x))
        return df[['team_number', 'rank', 'record']]
    else:
        df =  pd.DataFrame()
        df = zero_if_column_missing(df, 'team_number')
        return df


def get_event_oprs(event_key):

    r = _get("/event/{event_key}/oprs".format(event_key=event_key), result_type='text')
    df = pd.read_json(r, orient='columns').reset_index()
    df['team_number'] = df['index'].apply(team_number_from_key)

    df = zero_if_column_missing(df,'oprs')
    df = zero_if_column_missing(df, 'dprs')
    df = zero_if_column_missing(df, 'ccwms')
    df = zero_if_column_missing(df, 'team_number')

    df = df[['team_number', 'oprs', 'dprs', 'ccwms']]
    df.columns = ['team_number', 'opr', 'dpr', 'ccwm']
    return df


@cachetools.func.ttl_cache(maxsize=128, ttl=60 * 10)
def get_all_pch_team_numbers():
    df = get_all_pch_rankings_df()
    return list(df['team_number'])

@cachetools.func.ttl_cache(maxsize=128, ttl=60 * 10)
def get_all_pch_team_df():
    df = get_all_pch_rankings_df()
    return df

@cachetools.func.ttl_cache(maxsize=128, ttl=60 * 10)
def get_all_pch_rankings_df():
    # use the list of PCH teams
    r = _get("/district/{district_key}/rankings".format(district_key=Keys.PCH_DISTRICT))
    df = pd.DataFrame(r)
    df['team_number'] = df['team_key'].apply(team_number_from_key)
    df.rename(inplace=True, columns={
        'rank': 'district_rank',
        'event_points': 'district_points'
    })
    return df[['team_number','district_rank','point_total','team_key']]


# not documented, but it is in seconds
@cachetools.func.ttl_cache(maxsize=128, ttl=30)
def get_tba_team_stats(event_name):
    print("Getting event key",event_name)
    oprs = get_event_oprs(event_name)
    ranks = get_event_rankings(event_name)
    return pd.merge(ranks, oprs, on='team_number', how='outer', suffixes=('_event', '_opr'))


def get_tba_team_stats_for_team_current_event(team_number):
    return get_tba_team_stats_for_team(current_config['tba']['tba_event_key'],team_number)

# not documented, but it is in seconds
@cachetools.func.ttl_cache(maxsize=128, ttl=30)
def get_tba_teams_for_event(event_name):
    # use the list of PCH teams
    r = _get("/event/{event_key}/teams".format(event_key=event_name))
    df = pd.DataFrame(r)
    #df['team_number'] = df['team_key'].apply(team_number_from_key)
    df.rename(inplace=True, columns={
        'rank': 'district_rank',
        'event_points': 'district_points'
    })
    return df

def get_tba_team_stats_for_team(event_name, team_number):
    df = get_tba_team_stats("2024gacmp")
    r = df[df['team_number'] == team_number].to_dict(orient='records')
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
