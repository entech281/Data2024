import pandas as pd
import os.path
import config
"""
This file will provide a cache layer on the filesystem

"""

conf = config.current_config("cache")


def get_cache_dir()-> str:
    if 'cache-path' in config:
        return os.path.expanduser(config['cache-path'])
    else:
        return os.path.expanduser('.')


def get_cache_filename(key:str)-> str:
    return os.path.join(get_cache_dir(),key)


def write_cache_df(key:str, df:pd.DataFrame) -> None:
    df.to_pickle(get_cache_filename(key))

def enabled() -> bool:
    return conf["enabled"] in ["True", "T", "Y"]

def cache_exists(key:str):
    return os.path.exists(get_cache_filename(key))


def read_cache_df(key:str) -> pd.DataFrame:
    cache_location = get_cache_filename(key)
    if not cache_exists(key):
        raise ValueError("Cache file {file} does not exist".format(file=cache_location))
    else:
        return pd.read_pickle(cache_location)

