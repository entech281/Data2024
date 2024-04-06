import streamlit as st
import team_analysis
import tba
import gsheet_backend
import pandas as pd
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import cachetools.func

TBA_EVENT_KEY = None
CACHE_SECONDS = 600


# TODO: move to in UI uitility class
def write_markdown_list(vals):
    s = ""
    for v in vals:
        s += ("* " + v + "___" + "\n")
    return s

# TODO: move to in UI uitility class
def get_accuracy_colormap():
    c = ["darkred", "red", "lightcoral", "white", "palegreen", "green", "darkgreen"]
    v = [0, .15, .4, .5, 0.6, .9, 1.]
    l = list(zip(v, c))
    cmap = LinearSegmentedColormap.from_list('rg', l, N=256)
    return cmap


@cachetools.func.ttl_cache(maxsize=128, ttl=CACHE_SECONDS)
def load_match_data():
    raw_data = gsheet_backend.get_match_data()
    return team_analysis.analyze(raw_data)


@cachetools.func.ttl_cache(maxsize=128, ttl=CACHE_SECONDS)
def load_pit_data():
    raw_data = gsheet_backend.get_pits_data()
    return raw_data


def get_tag_manager():
    return gsheet_backend.get_tag_manager()

# TODO: move to gsheet_backend
@cachetools.func.ttl_cache(maxsize=128, ttl=CACHE_SECONDS)
def pit_data_for_team(team_num):
    all_data = load_pit_data()
    team_data = all_data[all_data['team.number'] == team_num]
    if len(team_data) > 0:
        return team_data.to_dict(orient='records')[0]
    else:
        return {}

@cachetools.func.ttl_cache(maxsize=128, ttl=CACHE_SECONDS*5)
def get_all_joined_team_data():
    all_pch_teams = tba.get_all_pch_team_df()
    all_pch_team_rankings = tba.get_all_pch_rankings_df()
    #print("District rankings df =",all_pch_team_rankings)
    pit_data = gsheet_backend.get_pits_data()
    tag_data = gsheet_backend.get_tag_manager().get_tags_by_team()
    raw_data = gsheet_backend.get_match_data()
    (analyzed_data,summary_data) = team_analysis.analyze(raw_data)
    #print("step 1,",summary_data)
    s = pd.merge(all_pch_teams,all_pch_team_rankings,on="team_number", how='outer', suffixes=('_pch','_rankings'))
    a = pd.merge(s, summary_data, on='team_number', how='outer', suffixes=('_pch', '_summary'))
    b = pd.merge(a, pit_data, on='team_number', how='outer', suffixes=('_pch', '_pit'))
    c = pd.merge(b, tag_data, on='team_number', how='outer', suffixes=('_pch', '_tag'))

    # teams with no rank get 999, for sorting purposes
    if 'rank' not in c.columns:
        c['rank'] = 0
    if 'rank_by_avg_pts' not in c.columns:
        c['rank_by_avg_pts'] = 0

    c['rank'].replace(np.nan, 999, inplace=True)
    c['rank_by_avg_pts'].replace(np.nan, 999, inplace=True)

    c['tag_list'].fillna({})
    #print("All Team Data=",c)
    c['team.number'] = c['team_number']
    return (analyzed_data, c)
