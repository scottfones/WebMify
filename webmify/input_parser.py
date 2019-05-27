import re

from typing import Tuple
from pathlib import Path, PurePath


def check_strip_path(file: str) -> str:
    if isinstance(file, PurePath):
        return file.name
    else:
        return Path(file).name


def get_title(file: str) -> str:
    file = check_strip_path(file)

    title_re = re.compile('^(.+?)[(.]')
    title_found = title_re.search(file).groups()[0]

    return title_found


def get_season(file: str) -> str:
    file = check_strip_path(file)

    season_re = re.compile('\W[s,S]([0-9]+)')
    season_groups = season_re.search(file)

    if season_groups is None:
        season_found = ''
    else:
        season_found = season_groups.groups()[0]

        if int(season_found) < 10 and season_found[0] != '0':
            season_found = '0' + season_found

    return season_found


def get_episode(file: str) -> str:
    file = check_strip_path(file)

    episode_re = re.compile('\d[e,E]([0-9]+)')
    episode_groups = episode_re.search(file)

    if episode_groups is None:
        episode_found = ''
    else:
        episode_found = episode_groups.groups()[0]

        if int(episode_found) < 10 and episode_found[0] != '0':
            episode_found = '0' + episode_found

    return episode_found


def get_season_episode(file: str) -> Tuple[str, str]:
    return (get_season(file), get_episode(file))


def get_title_season_episode(file: str) -> Tuple[str, str, str]:
    return (get_title(file),
            get_season(file),
            get_episode(file))


def is_movie(file: str) -> bool:
    season_num, ep_num = get_season_episode(file)

    if not season_num and not ep_num:
        return True
    else:
        return False