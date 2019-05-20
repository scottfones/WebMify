import sys
import api_keys
import tmdbsimple as tmdb


tmdb.API_KEY = api_keys.tmdb_key


def get_choice(search_response: dict) -> dict:
    print('\nMultiple matches found. Select from:')

    for index, result in enumerate(search_response['results']):
        try:
            print(f"[{index}]: {result['name']}, {result['first_air_date'][:4]} (https://www.themoviedb.org/tv/{result['id']})")
        except KeyError:
            print(f"[{index}]: {result['title']}, {result['release_date'][:4]} (https://www.themoviedb.org/movie/{result['id']})")

    user_choice = input('Result number: ')

    return search_response['results'][int(user_choice)]


def find_movie(title: str) -> dict:
    search = tmdb.Search()
    return search.movie(query=title)


def find_tv(title: str) -> dict:
    search = tmdb.Search()
    return search.tv(query=title)


def find_tv_episode(media_info: dict, season_num: str, episode_num: str) -> dict:
    return tmdb.TV_Episodes(media_info['id'],
                            int(season_num),
                            int(episode_num)).info()


def get_tv_metadata(show_info: dict, ep_info: dict) -> tuple:
    return (show_info['name'], ep_info['name'], ep_info['overview'])


def display_movie(movie_info: dict):
    print(f"\nMovie URL:\nhttps://www.themoviedb.org/movie/{movie_info['id']}")
    print('\nMovie Info:')
    print(f"Title: {movie_info['title']}")
    print(f"Release Date: {movie_info['release_date']}")
    print(f"Synopsis: {movie_info['overview']}")


def display_tv_episode(show_info: dict, ep_info: dict):
    print(f"\nEpisode URL:\nhttps://www.themoviedb.org/tv/{show_info['id']}/season/{ep_info['season_number']}/episode/{ep_info['episode_number']}")
    print('\nEpisode Info:')
    print(f"Show: {show_info['name']}")
    print(f"Season: {ep_info['season_number']}")
    print(f"Episode: {ep_info['episode_number']}")
    print(f"Air Date: {ep_info['air_date']}")
    print(f"Episode Title: {ep_info['name']}")
    print(f"Episode Overview: {ep_info['overview']}")


def look_up(title: str, season_num: str='', episode_num: str='') -> list:
    print(f'\nTMDb Look-up: {title}')

    if season_num == '' or episode_num == '':
        search_response = find_movie(title)
    else:
        search_response = find_tv(title)

    if search_response['total_results'] == 0:
        sys.exit('No match found. Try modifying the title flag.')
    elif search_response['total_results'] == 1:
        media_info = search_response['results'][0]
    else:
        media_info = get_choice(search_response)

    if season_num == '':
        display_movie(media_info)

        return [media_info]
    else:
        ep_info = find_tv_episode(media_info,
                                  season_num,
                                  episode_num)

        display_tv_episode(media_info, ep_info)

        return [media_info, ep_info]
