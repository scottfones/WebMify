api_key = ''


def get_key():
    assert(len(api_key) > 0), 'tmdb_key.py: API key not present.'
    return(api_key)
