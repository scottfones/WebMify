import stream_helpers

from pathlib import Path, PurePath
from typing import Dict, List, Tuple, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


lang_dict = {'chi': 'Chinese',
             'eng': 'English',
             'fre': 'French',
             'ger': 'German',
             'jpn': 'Japanese',
             'spn': 'Spanish'}
"""Communal dict to translate language codes."""


@dataclass
class StreamObject(ABC):
    """Abstract base class for all streams.

    Attributes and methods span audio, video and subtitle
    streams. Each has its own abstract, derived class.

    All streams track their own ffmpeg parameters in list
    variables to ease collection for ffmpeg's system call.

    Attributes:
        in_file: source file containing the stream
        stream_id: id number of stream relative to
                   the first stream of that type
        stream_maps: list of map flags to pass to ffmpeg
                     ex. ['-map', '0:v:0']
        filter_flags: list of processing flags to pass to ffmpeg
                      ex. ['-af', '"channelmap=channel_layout=stereo"']
        encoder_flags: list of encoder options to pass to ffmpeg
                       ex. ['-c:a:0', 'libopus', '-b:a:0', '128k']
        metadata: list of metadata flags to pass to ffmpeg
                  ex. ['-metadata', 'title="Stream Title"']
    """
    in_file: PurePath
    stream_id: str
    stream_maps: List[str] = field(init=False)
    filter_flags: List[str] = field(init=False)
    encoder_flags: List[str] = field(init=False)
    metadata: List[str] = field(init=False)

    def __post_init__(self):
        """Call concrete methods to finalize attributes."""
        self._set_stream_maps()
        self._set_filter()
        self._set_encoder()
        self._set_metadata()

    @abstractmethod
    def _set_stream_maps(self) -> None:
        pass

    @abstractmethod
    def _set_filter(self) -> None:
        pass

    @abstractmethod
    def _set_encoder(self) -> None:
        pass

    @abstractmethod
    def _set_metadata(self) -> None:
        pass


@dataclass
class AudioStream(StreamObject, ABC):
    """Abstract base class for all classes handling audio streams.

    Attributes:
        stream_lang: 3 letter language code
    """
    stream_lang: str = None

    def __post_init__(self):
        """Audio streams must track the number of channels and their
        language before defining the rest of their attributes.
        """
        self.channel_num = stream_helpers.get_audio_ch(self.in_file,
                                                       self.stream_id)
        if not self.stream_lang:
            self.stream_lang = stream_helpers.get_audio_lang(self.in_file,
                                                             self.stream_id)

        super().__post_init__()

    def _set_stream_maps(self):
        if int(self.channel_num) < 6:
            self.stream_maps = ['-map', f'0:a:{self.stream_id}']
        else:
            self.stream_maps = ['-map', '"[ss]"']


@dataclass
class NormalizedFirstPassStream(AudioStream):
    def _set_filter(self):
        self.filter_flags = ['-af', 'loudnorm=I=-16:LRA=16:tp=-1.5:'
                                    'print_format=json']

    def _set_encoder(self):
        pass

    def _set_metadata(self):
        self.metadata = ['-f', 'null']


@dataclass
class NormalizedSecondPassStream(AudioStream):
    norm_i: str = ''
    norm_tp: str = ''
    norm_lra: str = ''
    norm_thresh: str = ''
    norm_tar_off: str = ''

    def _set_filter(self):
        self.filter_flags = ['-af', 'loudnorm=I=-16:LRA=16:tp=-1.5:'
                                    f'measured_I={self.norm_i}:'
                                    f'measured_LRA={self.norm_lra}:'
                                    f'measured_tp={self.norm_tp}:'
                                    f'measured_thresh={self.norm_tar_off}:'
                                    f'offset={self.norm_tar_off}:'
                                    'print_format=json']

    def _set_encoder(self):
        self.encoder_flags = ['-c:a', 'pcm_s16le', '-ar', '48k']

    def _set_metadata(self):
        self.metadata = ['-metadata:s:a', f'title="{lang_dict[self.stream_lang]} '
                                          '- Normalized Stereo"']


@dataclass
class OpusStream(AudioStream):
    # Bitrates from: https://wiki.xiph.org/index.php?title=Opus_Recommended_Settings
    def _set_filter(self):
        filter_dict = {'1': ['-af', 'channelmap=channel_layout=mono'],
                       '2': ['-af', 'channelmap=channel_layout=stereo'],
                       '4': ['-ac', '2'],
                       '6': ['-filter_complex', f'"[a:{self.stream_id}]'
                                                f'[a:{self.stream_id}]'
                                                'channelmap=channel_layout=5.1'
                                                '[ss]"'],
                       '8': ['-filter_complex', f'"[a:{self.stream_id}]'
                                                f'[a:{self.stream_id}]'
                                                'channelmap=channel_layout=7.1'
                                                '[ss]"']}

        self.filter_flags = filter_dict[self.channel_num]

    def _set_encoder(self):
        encoder_dict = {'1': ['-c:a', 'libopus', '-b:a', '96k'],
                        '2': ['-c:a', 'libopus', '-b:a', '128k'],
                        '4': ['-c:a', 'libopus', '-b:a', '128k'],
                        '6': ['-c:a', 'libopus', '-b:a', '256k'],
                        '8': ['-c:a', 'libopus', '-b:a', '450k']}

        self.encoder_flags = encoder_dict[self.channel_num]

    def _set_metadata(self):
        metadata_dict = {'1': ['-metadata:s:a', f'title="{lang_dict[self.stream_lang]} '
                                                '- Opus Mono - 96kbps"',
                               '-metadata:s:a', f'language={self.stream_lang}'],
                         '2': ['-metadata:s:a', f'title="{lang_dict[self.stream_lang]} '
                                                '- Opus Stereo - 128kbps"',
                               '-metadata:s:a', f'language={self.stream_lang}'],
                         '4': ['-metadata:s:a', f'title="{lang_dict[self.stream_lang]} '
                                                '- Opus Stereo - 128kbps"',
                               '-metadata:s:a', f'language={self.stream_lang}'],
                         '6': ['-metadata:s:a', f'title="{lang_dict[self.stream_lang]} '
                                                '- Opus Surround Sound - 5.1 - 256kbps"',
                               '-metadata:s:a', f'language={self.stream_lang}'],
                         '8': ['-metadata:s:a', f'title="{lang_dict[self.stream_lang]} '
                                                '- Opus Surround Sound - 7.1 - 450kbps"',
                               '-metadata:s:a', f'language={self.stream_lang}']}

        self.metadata = metadata_dict[self.channel_num]


@dataclass
class OpusNormalizedDownmixStream(OpusStream):
    def _set_metadata(self):
        self.metadata = ['-metadata:s:a', f'title="{lang_dict[self.stream_lang]} '
                                          '- Opus Normalized Downmix - 2.0 - 128kbps"',
                         '-metadata:s:a', f'language={self.stream_lang}']


@dataclass
class StereoDownmixStream(AudioStream):
    def _set_filter(self):
        self.filter_flags = ['-filter_complex', f'[a:{self.stream_id}]'
                                                'pan=stereo'
                                                '|c0=.9*FL+1.10*FC+.4*BL+.4*SL'
                                                '|c1=.9*FR+1.10*FC+.4*BR+.4*SR'
                                                '[dm]']

    def _set_encoder(self):
        self.encoder_flags = ['-c:a', 'pcm_s16le', '-ar', '48k']

    def _set_metadata(self):
        self.metadata = ['-metadata:s:a', f'title="{lang_dict[self.stream_lang]} '
                                          '- Stereo Downmix"',
                         '-metadata:s:a', f'language={self.stream_lang}']

    def _set_stream_maps(self):
        self.stream_maps = ['-map', '[dm]']
