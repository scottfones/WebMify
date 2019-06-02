import subprocess
from pathlib import Path
from collections import Counter


def get_audio_ch(input_file: str, audio_id: str) -> str:
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


def get_audio_lang(input_file: str, audio_id: str) -> str:
    """Use ffprobe to query the language of
    the specified audio stream.

    Parameters:
    input_file - filename, string or Path()
    audi_id - relative audio stream id [0...]
    """
    audio_lang_probe_cmd = ['ffprobe', f'{input_file}', '-loglevel',
                            'error', '-select_streams', f'a:{audio_id}', 
                            '-show_entries', 'stream_tags=language',
                            '-of', 'default=nw=1:nk=1']

    return subprocess.check_output(audio_lang_probe_cmd, stdin=None,
                                   stderr=None, shell=False,
                                   universal_newlines=True).strip()
