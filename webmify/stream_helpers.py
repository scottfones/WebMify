import subprocess
from pathlib import Path, PurePath
from collections import Counter


def get_audio_ch(in_file: PurePath, audio_id: str) -> str:
    """Use ffprobe to query the number of
    audio channels in the specified stream.

    Parameters:
    in_file - filename, string or Path()
    audio_id - relative audio stream id [0...]
    """
    probe_cmd = ['ffprobe', f'{in_file}', '-loglevel', 'error',
                 '-select_streams', f'a:{audio_id}', '-show_entries',
                 'stream=channels', '-of', 'default=nw=1:nk=1']

    return subprocess.check_output(probe_cmd, stdin=None, stderr=None,
                                   shell=False, universal_newlines=True).strip()


def get_audio_lang(in_file: PurePath, audio_id: str) -> str:
    """Use ffprobe to query the language of
    the specified audio stream.

    Parameters:
    in_file - filename
    audio_id - relative audio stream id [0...]
    """
    audio_lang_probe_cmd = ['ffprobe', f'{in_file}', '-loglevel',
                            'error', '-select_streams', f'a:{audio_id}',
                            '-show_entries', 'stream_tags=language',
                            '-of', 'default=nw=1:nk=1']

    return subprocess.check_output(audio_lang_probe_cmd, stdin=None,
                                   stderr=None, shell=False,
                                   universal_newlines=True).strip()


def get_height(in_file: PurePath, stream_id: str) -> int:
    """Use ffprobe to query the height of
    the specified video stream. Returns int
    of resolution height.

    Parameters:
    in_file - filename
    stream_id - relative video stream id [0...]
    """
    probe_cmd = ['ffprobe', f'{in_file}', '-loglevel',
                            'error', '-select_streams', f'v:{stream_id}',
                            '-show_entries', 'stream=height',
                            '-of', 'default=nw=1:nk=1']

    height = subprocess.check_output(probe_cmd, stdin=None,
                                     stderr=None, shell=False,
                                     universal_newlines=True).strip()

    return int(height)


def get_sub_stream(in_file: PurePath) -> str:
    """Use ffprobe to query for subtitle stream
    ids.

    Parameters:
    in_file - filename
    """
    probe_cmd = ['ffprobe', f'{in_file}', '-loglevel',
                 'error', '-select_streams', 's:m:language=eng',
                 '-show_entries', 'stream=index', '-of', 'csv=p=0']

    return subprocess.check_output(probe_cmd, stdin=None, stderr=None,
                                   shell=False, universal_newlines=True).strip()


def get_vp9_tile_columns(in_file: PurePath, stream_id: str) -> str:
    """Use ffprobe to query the resolution of
    the specified video stream and return the
    recommended number of tile columns.

    Recommendations from:
    https://developers.google.com/media/vp9/settings/vod/

    Parameters:
    in_file - filename
    stream_id - relative video stream id [0...]
    """
    height = get_height(input_file, stream_id)

    if height <= 240:
        return '0'
    elif height <= 480:
        return '1'
    elif height <= 1080:
        return '2'
    elif height <= 1440:
        return '3'
    else:
        return '4'


def is_hdr(in_file: PurePath, stream_id: str) -> bool:
    """Use ffprobe to query the color space of
    the specified video stream and return True
    if bt2020nc.

    Parameters:
    input_file - filename
    stream_id - relative video stream id [0...]
    """
    probe_cmd = ['ffprobe', f'{in_file}', '-loglevel',
                            'error', '-select_streams', f'v:{stream_id}',
                            '-show_entries', 'stream=color_space',
                            '-of', 'default=nw=1:nk=1']

    color_space = subprocess.check_output(probe_cmd, stdin=None,
                                          stderr=None, shell=False,
                                          universal_newlines=True).strip()

    return color_space == 'bt2020nc'
