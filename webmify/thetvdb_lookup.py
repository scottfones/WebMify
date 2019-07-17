import sys
import tvdb_api
import api_keys

from typing import List, NoReturn, Tuple
from tvdb_api import tvdb_shownotfound, tvdb_seasonnotfound, tvdb_episodenotfound


def display_episode(title: str, s_num: str, ep_num: str, episode: dict) -> NoReturn:
    print(f'Show: {title}')
    print(f'Season: {s_num}')
    print(f'Episode: {ep_num}')
    print(f"Summary: {episode['episodeName']}")


def get_title(title: str) -> str:
    tvdb = tvdb_api.Tvdb(apikey=api_keys.thetvdb_key, interactive=True)

    try:
        show = tvdb[title]
    except tvdb_shownotfound:
        print(f"Show '{title}' not found. Please enter a valid show title:'")
        show_input = input()

        show_title = get_tv_title(show_input)
        return(show_title)

    return show['seriesName']


def get_file_metadata(title: str, s_num: str, ep_num: str) -> str:
    tvdb = tvdb_api.Tvdb(apikey=api_keys.thetvdb_key)

    try:
        episode = tvdb[title][int(s_num)][int(ep_num)]
    except tvdb_seasonnotfound:
        sys.exit("TV Season '{s_num}' not found. Try modifying the season with the --season flag.")
    except tvdb_episodenotfound:
        sys.exit("TV Episode '{ep_num}' not found. Try modifying the season with the --episode flag.")

    display_episode(title, s_num, ep_num, episode)

    return (f"{title} - S{s_num}E{ep_num} - {episode['episodeName']}",
            episode['overview'])
