import sys
import tvdb_api
import api_keys

from typing import List, NoReturn, Tuple
from tvdb_api import tvdb_shownotfound, tvdb_seasonnotfound, tvdb_episodenotfound


def get_tv_title(title: str) -> str:
    tvdb = tvdb_api.Tvdb(apikey=api_keys.thetvdb_key, interactive=True)

    try:
        show = tvdb[title]
    except tvdb_shownotfound:
        print(f"Show '{title}' not found. Please enter a valid show title:'")
        show_input = input()

        show_title = get_tv_title(show_input)
        return(show_title)

    return show['seriesName']


def get_tv_info(title: str, s_num: str, ep_num: str) -> Tuple[str, str, str, str]:
    tvdb = tvdb_api.Tvdb(apikey=api_keys.thetvdb_key)

    try:
        episode = tvdb[title][int(s_num)][int(ep_num)]
    except tvdb_seasonnotfound:
        sys.exit("TV Season '{s_num}' not found. Try modifying the season with the --season flag.")
    except tvdb_episodenotfound:
        sys.exit("TV Episode '{ep_num}' not found. Try modifying the season with the --episode flag.")

    return (episode['episodeName'], episode['overview'].strip(), episode['firstAired'])
