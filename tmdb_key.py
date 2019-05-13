api_key = '01a09891363e68e9dfcfa846cf1e1031'


def get_key():
    assert(len(api_key) > 0), 'tmdb_key.py: API key not present.'
    return(api_key)
