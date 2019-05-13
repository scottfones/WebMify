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


def find_tv(title, season_um, episode_num):
    search = tmdb.Search()
    return search.tv(query=title)


def display_result(media_parent):
    print('TBDb Info:')
    try:
        print(f"  Title: {media_parent['name']}")
    except KeyError:
        print(f"  Title: {media_parent['title']}")
    print(f"  Synopsis: {media_parent['overview']}")


def look_up(title, season_num='', episode_num=''):
    print('TMDb Look-up:')
    if season_num == '' or episode_num == '':
        search_response = find_movie(title)
    else:
        search_response = find_tv(title, season_num, episode_num)

    if search_response['total_results'] > 1:
        media_parent = get_choice(search_response)
    else:
        media_parent = search_response['results'][0]

    display_result(media_parent)
