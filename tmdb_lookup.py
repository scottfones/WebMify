import tmdb_key
import tmdbsimple as tmdb


tmdb.API_KEY = tmdb_key.get_key()


def get_choice(search_response):
    print('\nMultiple matches found. Select from:')

    for index, result in enumerate(search_response['results']):
        try:
            print(f"[{index}]: {result['name']}, {result['first_air_date'][:4]} (https://www.themoviedb.org/tv/{result['id']})")
        except KeyError:
            print(f"[{index}]: {result['title']}, {result['release_date'][:4]} (https://www.themoviedb.org/movie/{result['id']})")
        # print(f"[{index}]: {result['name']}")
        # print(f"[{index}]")

    user_choice = input('Result number: ')

    return search_response['results'][int(user_choice)]


def find_movie(title):
    search = tmdb.Search()
    return search.movie(query=title)


def find_tv(title):
    search = tmdb.Search()
    return search.tv(query=title)


def find_tv_episode(media_info, season_num, episode_num):
    return tmdb.TV_Episodes(media_info['id'],
                            int(season_num),
                            int(episode_num)).info()


def display_movie(movie_info):
    print(f"\nMovie URL:\nhttps://www.themoviedb.org/movie/{movie_info['id']}")
    print('\nMovie Info:')
    print(f"Title: {movie_info['title']}")
    print(f"Release Date: {movie_info['release_date']}")
    print(f"Synopsis: {movie_info['overview']}")


def display_tv_episode(show_info, ep_info):
    print(f"\nEpisode URL:\nhttps://www.themoviedb.org/tv/{show_info['id']}/season/{ep_info['season_number']}/episode/{ep_info['episode_number']}") 
    print('\nEpisode Info:')
    print(f"Show: {show_info['name']}")
    print(f"Season: {ep_info['season_number']}")
    print(f"Episode: {ep_info['episode_number']}")
    print(f"Air Date: {ep_info['air_date']}")
    print(f"Episode Title: {ep_info['name']}")
    print(f"Episode Overview: {ep_info['overview']}")


def look_up(title, season_num='', episode_num=''):
    print('TMDb Look-up:')
    if season_num == '' or episode_num == '':
        search_response = find_movie(title)
    else:
        search_response = find_tv(title)

    if search_response['total_results'] > 1:
        media_info = get_choice(search_response)
    else:
        media_info = search_response['results'][0]

    if season_num == '':
        display_movie(media_info)
    else:
        display_tv_episode(media_info,
                           find_tv_episode(media_info,
                                           season_num,
                                           episode_num))
