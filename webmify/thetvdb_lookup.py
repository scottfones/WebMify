import tvdb_api
import api_keys

from typing import List, NoReturn, Tuple


def get_tv_title(title: str) -> str:
    tvdb = tvdb_api.Tvdb(apikey=api_keys.thetvdb_key, interactive=True)
    show = tvdb[title]

    return show['seriesName']


def get_tv_info(title: str, s_num: str, ep_num: str) -> Tuple[str, str, str, str]:
    tvdb = tvdb_api.Tvdb(apikey=api_keys.thetvdb_key)
    episode = tvdb[title][int(s_num)][int(ep_num)]

    return (episode['episodeName'], episode['overview'], episode['firstAired'])
