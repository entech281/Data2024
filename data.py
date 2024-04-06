import pandas as pd

import gsheet_backend
import df_cache
import cachetools.func
"""
Fetch data for the application.
this is where we use a backend, and
also caching as applicable
"""
CACHE_SECONDS = 600
class SheetTabs:
    MATCHES = "DCMP Matches"
    PITS = "DCMP Pits"


def get_sheet_tab_with_cache(tab_name:str) -> pd.DataFrame:
    if df_cache.enabled() and df_cache.cache_exists(tab_name):
        return df_cache.read_cache_df(tab_name)

    return gsheet_backend.read_data_on_tab(tab_name)


@cachetools.func.ttl_cache(maxsize=128, ttl=CACHE_SECONDS)
def get_match_data():
    return get_sheet_tab_with_cache(SheetTabs.MATCHES)


@cachetools.func.ttl_cache(maxsize=128, ttl=CACHE_SECONDS)
def get_pit_data():
    df = get_sheet_tab_with_cache(SheetTabs.PITS)
    most_recent_row_per_team = df[df.groupby('team.number')['tstamp'].transform('max') == df['tstamp']]
    most_recent_row_per_team['team_number'] = most_recent_row_per_team['team.number']
    return most_recent_row_per_team
