import sys
import api_keys
import tmdbsimple as tmdb

from typing import List, NoReturn, Tuple


tmdb.API_KEY = api_keys.tmdb_key


def get_choice(search_response: dict) -> dict:
    """Obtain user choice for multiple search results.
    Return specified result.

    Parameters:
    search_response -- raw search return from TMDb
    """
    print('\nMultiple matches found. Select from:')

    for index, result in enumerate(search_response['results']):
        try:
            print(f"[{index}]: {result['name']}, "
                  f"{result['first_air_date'][:4]} "
                  f"(https://www.themoviedb.org/tv/{result['id']})")
        except KeyError:
            print(f"[{index}]: {result['title']}, "
                  f"{result['release_date'][:4]} "
                  f"(https://www.themoviedb.org/movie/{result['id']})")

    user_choice = input('Result number: ')

    return search_response['results'][int(user_choice)]


def find_movie(title: str) -> dict:
    """TMDb movie specific search.
    Returns unprocessed api return.

    Parameters:
    title - movie title for query
    """
    search = tmdb.Search()
    return search.movie(query=title)


def display_movie(movie_info: dict) -> NoReturn:
    """Display movie information"""
    print(f"\nMovie URL:\nhttps://www.themoviedb.org/movie/{movie_info['id']}")
    print('\nMovie Info:')
    print(f"Title: {movie_info['title']}")
    print(f"Release Date: {movie_info['release_date']}")
    print(f"Synopsis: {movie_info['overview']}")


def display_tv_episode(show_info: dict, ep_info: dict) -> NoReturn:
    """Display tv episode information"""
    print(f"\nEpisode URL:\nhttps://www.themoviedb.org/tv/"
          f"{show_info['id']}/season/{ep_info['season_number']}"
          f"/episode/{ep_info['episode_number']}")
    print('\nEpisode Info:')
    print(f"Show: {show_info['name']}")
    print(f"Season: {ep_info['season_number']}")
    print(f"Episode: {ep_info['episode_number']}")
    print(f"Air Date: {ep_info['air_date']}")
    print(f"Episode Title: {ep_info['name']}")
    print(f"Episode Overview: {ep_info['overview']}")


def get_movie_info(title: str) -> Tuple[str, str, str]:
    search_response = find_movie(title)

    if search_response['total_results'] == 0:
        sys.exit('No match found. Try modifying the title flag.')
    elif search_response['total_results'] == 1:
        movie_info = search_response['results'][0]
    else:
        movie_info = get_choice(search_response)

    return (movie_info['title'],
            movie_info['release_date'],
            movie_info['overview'])
