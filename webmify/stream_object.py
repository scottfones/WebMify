import settings
import stream_helpers

import sys
from pathlib import Path, PurePath
from typing import Dict, List, Tuple, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


lang_dict = {'chi': 'Chinese',
             'eng': 'English',
             'fre': 'French',
             'ger': 'German',
             'jpn': 'Japanese',
             'spn': 'Spanish',
             'und': '',
             '': 'English'}
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
            self.stream_maps = ['-map', '[ss]']


@dataclass
class AACStream(AudioStream):
    # Bitrates from: https://trac.ffmpeg.org/wiki/Encode/AAC vbr esimations
    def _set_filter(self):
        filter_dict = {'1': ['-af', 'channelmap=channel_layout=mono'],
                       '2': ['-af', 'channelmap=channel_layout=stereo'],
                       '4': ['-ac', '2'],
                       '6': ['-filter_complex', f'[a:{self.stream_id}]'
                                                'channelmap=channel_layout=5.1'
                                                '[ss]'],
                       '8': ['-filter_complex', f'[a:{self.stream_id}]'
                                                'channelmap=channel_layout=7.1'
                                                '[ss]']}

        self.filter_flags = filter_dict[self.channel_num]

    def _set_encoder(self):
        encoder_dict = {'1': ['-c:a', 'libfdk_aac', '-b:a', '96k', '-cutoff', '18000'],
                        '2': ['-c:a', 'libfdk_aac', '-b:a', '192k', '-cutoff', '18000'],
                        '4': ['-c:a', 'libfdk_aac', '-b:a', '192k', '-cutoff', '18000'],
                        '6': ['-c:a', 'libfdk_aac', '-b:a', '480k', '-cutoff', '18000'],
                        '8': ['-c:a', 'libfdk_aac', '-b:a', '672k', '-cutoff', '18000']}

        self.encoder_flags = encoder_dict[self.channel_num]

    def _set_metadata(self):
        metadata_dict = {'1': ['-metadata:s:a', f'title={lang_dict[self.stream_lang]} '
                                                '- AAC Mono',
                               '-metadata:s:a', f'language={self.stream_lang}'],
                         '2': ['-metadata:s:a', f'title={lang_dict[self.stream_lang]} '
                                                '- AAC Stereo',
                               '-metadata:s:a', f'language={self.stream_lang}'],
                         '4': ['-metadata:s:a', f'title={lang_dict[self.stream_lang]} '
                                                '- Opus Stereo',
                               '-metadata:s:a', f'language={self.stream_lang}'],
                         '6': ['-metadata:s:a', f'title={lang_dict[self.stream_lang]} '
                                                '- AAC Surround Sound - 5.1',
                               '-metadata:s:a', f'language={self.stream_lang}'],
                         '8': ['-metadata:s:a', f'title={lang_dict[self.stream_lang]} '
                                                '- AAC Surround Sound - 7.1',
                               '-metadata:s:a', f'language={self.stream_lang}']}

        self.metadata = metadata_dict[self.channel_num]


@dataclass
class AACNormalizedDownmixStream(AACStream):
    def _set_metadata(self):
        self.metadata = ['-metadata:s:a', f'title={lang_dict[self.stream_lang]} '
                                          '- AAC Dialogue Enhanced Downmix - 2.0',
                         '-metadata:s:a', f'language={self.stream_lang}']


@dataclass
class NormalizedFirstPassStream(AudioStream):
    def _set_filter(self):
        self.filter_flags = ['-af', 'loudnorm=I=-16:LRA=16:tp=-1.5:'
                                    'print_format=json']

    def _set_encoder(self):
        self.encoder_flags = None

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
                                    f'measured_thresh={self.norm_thresh}:'
                                    f'offset={self.norm_tar_off}:'
                                    'print_format=json']

    def _set_encoder(self):
        self.encoder_flags = ['-c:a', 'pcm_s16le', '-ar', '48k']

    def _set_metadata(self):
        self.metadata = ['-metadata:s:a', f'title={lang_dict[self.stream_lang]} '
                                          '- Normalized Stereo']


@dataclass
class OpusStream(AudioStream):
    # Bitrates from: https://wiki.xiph.org/index.php?title=Opus_Recommended_Settings
    def _set_filter(self):
        filter_dict = {'1': ['-af', 'channelmap=channel_layout=mono'],
                       '2': ['-af', 'channelmap=channel_layout=stereo'],
                       '4': ['-ac', '2'],
                       '6': ['-filter_complex', f'[a:{self.stream_id}]'
                                                'channelmap=channel_layout=5.1'
                                                '[ss]'],
                       '8': ['-filter_complex', f'[a:{self.stream_id}]'
                                                'channelmap=channel_layout=7.1'
                                                '[ss]']}

        self.filter_flags = filter_dict[self.channel_num]

    def _set_encoder(self):
        encoder_dict = {'1': ['-c:a', 'libopus', '-b:a', '96k'],
                        '2': ['-c:a', 'libopus', '-b:a', '128k'],
                        '4': ['-c:a', 'libopus', '-b:a', '128k'],
                        '6': ['-c:a', 'libopus', '-b:a', '256k'],
                        '8': ['-c:a', 'libopus', '-b:a', '450k']}

        self.encoder_flags = encoder_dict[self.channel_num]

    def _set_metadata(self):
        metadata_dict = {'1': ['-metadata:s:a', f'title={lang_dict[self.stream_lang]} '
                                                '- Opus Mono',
                               '-metadata:s:a', f'language={self.stream_lang}'],
                         '2': ['-metadata:s:a', f'title={lang_dict[self.stream_lang]} '
                                                '- Opus Stereo',
                               '-metadata:s:a', f'language={self.stream_lang}'],
                         '4': ['-metadata:s:a', f'title={lang_dict[self.stream_lang]} '
                                                '- Opus Stereo',
                               '-metadata:s:a', f'language={self.stream_lang}'],
                         '6': ['-metadata:s:a', f'title={lang_dict[self.stream_lang]} '
                                                '- Opus Surround Sound - 5.1',
                               '-metadata:s:a', f'language={self.stream_lang}'],
                         '8': ['-metadata:s:a', f'title={lang_dict[self.stream_lang]} '
                                                '- Opus Surround Sound - 7.1',
                               '-metadata:s:a', f'language={self.stream_lang}']}

        self.metadata = metadata_dict[self.channel_num]


@dataclass
class OpusNormalizedDownmixStream(OpusStream):
    def _set_metadata(self):
        self.metadata = ['-metadata:s:a', f'title={lang_dict[self.stream_lang]} '
                                          '- Opus Dialogue Enhanced Downmix - 2.0',
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
        self.metadata = ['-metadata:s:a', f'title={lang_dict[self.stream_lang]} '
                                          '- Stereo Downmix',
                         '-metadata:s:a', f'language={self.stream_lang}']

    def _set_stream_maps(self):
        self.stream_maps = ['-map', '[dm]']


###################################
#                                 #
#        Subtitle Streams         #
#                                 #
###################################

@dataclass
class WebVTTStream(StreamObject):
    def _set_filter(self):
        self.filter_flags = None

    def _set_encoder(self):
        self.encoder_flags = ['-c:s', 'webvtt']

    def _set_metadata(self):
        self.metadata = ['-metadata:s:s', 'title=English Subtitles']

    def _set_stream_maps(self):
        self.stream_maps = ['-map', f'0:s:{self.stream_id}']


###################################
#                                 #
#         Video Streams           #
#                                 #
###################################

@dataclass
class VideoStream(StreamObject, ABC):
    """Abstract base class for all classes handling video streams.

    """

    burn_subs: bool = False
    crop: bool = False
    cpu_threads: str = settings.cpu_threads
    crf: str = '19'
    denoise: bool = False
    hdr_to_sdr: bool = False
    scale_to_1080: bool = False
    scale_to_720: bool = False
    sub_file: PurePath = ''

    def _add_filter(self, tmp_filter: str):
        if len(self.filter_flags) == 1:
            self.filter_flags.append(self.tmp_filter)
        else:
            self.filter_flags[1] += self.tmp_filter

    def _filter_len_check(self):
        if len(self.filter_flags) == 2:
            self.filter_flags[1] += ','

    def _set_filter(self):
        self.any_filter = (self.crop or
                           self.burn_subs or
                           self.denoise or
                           self.hdr_to_sdr or
                           self.scale_to_1080 or
                           self.scale_to_720)

        if self.scale_to_1080 and self.scale_to_720:
            sys.exit('Mutually exclusive scaling options selected. '
                     'Choose either 1080p or 720p.')

        if self.any_filter:
            self.filter_flags = ['-vf']
        else:
            self.filter_flags = None

        if self.crop:
            print('\nParsing crop dimensions: ', end='')
            self.crop_dimns = stream_helpers.get_crop_dimns(self.in_file)
            print(f'{self.crop_dimns}')
            self.tmp_filter = f'crop={self.crop_dimns}'
            self._filter_len_check()
            self._add_filter(self.tmp_filter)

        if self.scale_to_1080:
            self.tmp_filter = 'scale=1920:-2'
            self._filter_len_check()
            self._add_filter(self.tmp_filter)

        if self.scale_to_720:
            self.tmp_filter = 'scale=1280:-2'
            self._filter_len_check()
            self._add_filter(self.tmp_filter)

        if self.hdr_to_sdr:
            self.tmp_filter = ('zscale=t=linear,format=gbrpf32le,'
                               'zscale=p=bt709,tonemap=tonemap='
                               'hable:desat=0.0,zscale=t=bt709:'
                               'm=bt709:r=tv,format=yuv420p')
            self._filter_len_check()
            self._add_filter(self.tmp_filter)

        if self.denoise:
            self.tmp_filter = 'fftdnoiz=10:1:5:0.5:1:1'
            self._filter_len_check()
            self._add_filter(self.tmp_filter)

        if self.burn_subs:
            self.sub_type = stream_helpers.get_sub_type(in_file=self.sub_file,
                                                        stream_id=self.stream_id)

            if self.sub_type == 'subrip':
                self.tmp_filter = (f"subtitles={self.sub_file}:force_style='"
                                   f"FontName={settings.sub_font_name},"
                                   f"Fontsize={settings.sub_font_size},"
                                   f"PrimaryColour={settings.sub_font_color}'")
            elif self.sub_type == 'ass':
                self.tmp_filter = f'subtitles={self.sub_file}'
            else:
                sys.exit(f'Subtitle type not currently supported: {self.sub_type}')
            self._filter_len_check()
            self._add_filter(self.tmp_filter)

    def _set_stream_maps(self):
        self.stream_maps = ['-map', f'0:v:{self.stream_id}']


@dataclass
class ChromecastStream(VideoStream):
    def __post_init__(self):
        self.hdr_to_sdr = stream_helpers.is_hdr(in_file=self.in_file,
                                                stream_id=self.stream_id)
        self.scale_to_1080 = (1080 < stream_helpers.get_height(in_file=self.in_file,
                                                               stream_id=self.stream_id))

        super().__post_init__()

    def _set_encoder(self):
        self.encoder_flags = ['-c:v', 'libx264', '-preset', 'veryslow', '-tune',
                              'film', '-crf', self.crf, '-profile:v', 'high',
                              '-level', '4.1', '-maxrate', '5M', '-bufsize', '2M']

    def _set_metadata(self):
        self.metadata = ['-metadata:s:v', 'title=h264 (avc1) 4.1 High']


@dataclass
class VP9Stream(VideoStream):
    def _set_encoder(self):
        self.tile_columns = stream_helpers.get_vp9_tile_columns(in_file=self.in_file,
                                                                stream_id=self.stream_id)

        self.encoder_flags = ['-c:v', 'libvpx-vp9', '-crf', self.crf, '-b:v',
                              '0', '-g', '240', '-deadline', 'good',
                              '-cpu-used', '2', '-tile-columns', self.tile_columns,
                              '-row-mt', '1', '-threads', settings.cpu_threads,
                              '-profile:v', '2', '-pix_fmt', 'yuv420p10le']

    def _set_metadata(self):
        self.metadata = ['-metadata:s:v', 'title=VP9 - Profile 2 - 10-bit']
