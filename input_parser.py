import re

from pathlib import Path


def get_title(file):
    print(f'\nParsing Title: {file}')

    title_re = re.compile('^(.+?)[(.]')
    title_found = title_re.search(file).groups()[0]

    print(f'Found: {title_found}')

    return title_found


def get_season(file):
    print(f'\nParsing Season: {file}')

    season_re = re.compile('[s,S]([0-9]+)')
    season_groups = season_re.search(file)

    if season_groups is None:
        season_found = ''
    else:
        season_found = season_groups.groups()[0]

    print(f'Found: {season_found}')

    return season_found


def get_episode(file):
    print(f'\nParsing Episode: {file}')

    episode_re = re.compile('[e,E]([0-9]+)')
    episode_groups = episode_re.search(file)

    if episode_groups is None:
        episode_found = ''
    else:
        episode_found = episode_groups.groups()[0]

    print(f'Found: {episode_found}')

    return episode_found
