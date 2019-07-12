import subprocess
from pathlib import Path, PurePath
from collections import Counter


def get_audio_ch(input_file: PurePath, audio_id: str) -> str:
    """Use ffprobe to query the number of
    audio channels in the specified stream.

    Parameters:
    input_file - filename, string or Path()
    audio_id - relative audio stream id [0...]
    """
    probe_cmd = ['ffprobe', f'{input_file}', '-loglevel', 'error',
                 '-select_streams', f'a:{audio_id}', '-show_entries',
                 'stream=channels', '-of', 'default=nw=1:nk=1']

    return subprocess.check_output(probe_cmd, stdin=None, stderr=None,
                                   shell=False, universal_newlines=True).strip()


def get_audio_lang(input_file: PurePath, audio_id: str) -> str:
    """Use ffprobe to query the language of
    the specified audio stream.

    Parameters:
    input_file - filename
    audio_id - relative audio stream id [0...]
    """
    audio_lang_probe_cmd = ['ffprobe', f'{input_file}', '-loglevel',
                            'error', '-select_streams', f'a:{audio_id}',
                            '-show_entries', 'stream_tags=language',
                            '-of', 'default=nw=1:nk=1']

    return subprocess.check_output(audio_lang_probe_cmd, stdin=None,
                                   stderr=None, shell=False,
                                   universal_newlines=True).strip()


def get_sub_stream(input_file: PurePath) -> str:
    """Use ffprobe to query for subtitle stream
    ids.

    Parameters:
    input_file - filename
    """
    probe_cmd = ['ffprobe', f'{input_file}', '-loglevel',
                 'error', '-select_streams', 's:m:language=eng',
                 '-show_entries', 'stream=index', '-of', 'csv=p=0']

    return subprocess.check_output(probe_cmd, stdin=None, stderr=None,
                                   shell=False, universal_newlines=True).strip()
