import re

from typing import Tuple
from pathlib import Path, PurePath


def check_strip_path(file: str) -> str:
    """Format input to string.
    Input may be Path() or str. Return only
    relevant infomation as str.
    """
    if isinstance(file, PurePath):
        return file.name
    else:
        return Path(file).name


def get_title(file: str) -> str:
    """Return the base filename, assumed
    to be the media title.

    Parameters:
    file -- Either string or Path() filename
    """
    file = check_strip_path(file)

    title_re = re.compile(r'^(.+?)[(.]')
    title_found = title_re.search(file).groups()[0]

    return title_found


def get_season(file: str) -> str:
    """Search and return season number as str.
    If none found, return empty string..

    Parameters:
    file -- Either string or Path() filename
    """
    file = check_strip_path(file)

    season_re = re.compile(r'\W[s,S]([0-9]+)')
    season_groups = season_re.search(file)

    if season_groups is None:
        season_found = ''
    else:
        season_found = season_groups.groups()[0]

        if int(season_found) < 10 and season_found[0] != '0':
            season_found = '0' + season_found

    return season_found


def get_episode(file: str) -> str:
    """Search and return episode number as str.
    If none found, return empty string..

    Parameters:
    file -- Either string or Path() filename
    """
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


def get_out_file(file: str, suffix: str) -> str:
    """Default output filename constructor.
    Removes file suffix and replace.
    """
    if isinstance(file, PurePath):
        return file.stem + suffix
    else:
        return Path(file).stem + suffix


def is_movie(file: str) -> bool:
    """Parse file name for season or episode
    information. If none is found, assume
    movie and return True.

    Parameters:
    file -- Either string or Path() filename
    """
    season_num = get_season(file)
    ep_num = get_episode(file)

    if not season_num and not ep_num:
        return True
    else:
        return False


def is_batch_repeat(file1: str, file2: str) -> bool:
    """Given two inputs, file1 and file2, return
    true if the parsed titles are equivalent.
    """
    
    if not file1 or not file2:
        return False

    title1 = get_title(file1)
    title2 = get_title(file2)

    return title1 == title2
