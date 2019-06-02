import stream_helpers

from pathlib import Path
from typing import Dict, List, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


lang_dict = {'chi': 'Chinese', 'eng': 'English', 'jpn': 'Japanese', 'spn': 'Spanish'}


@dataclass
class StreamObject(ABC):
    in_file: str
    stream_id: str
    stream_lang: str = None
    stream_maps: List[str] = field(init=False)
    filter_flags: List[str] = field(init=False)
    encoder_flags: List[str] = field(init=False)
    metadata: List[str] = field(init=False)

    def __post_init__(self):
        self.channel_num = stream_helpers.get_audio_ch(self.in_file,
                                                       self.stream_id)
        if not self.stream_lang:
            self.stream_lang = stream_helpers.get_audio_lang(self.in_file,
                                                             self.stream_id)

        self._set_stream_maps()
        self._set_filter()
        self._set_encoder()
        self._set_metadata()

    def _set_stream_maps(self):
        if self.channel_num == '1' or self.channel_num == '2':
            self.stream_maps = ['-map', f'0:a:{self.stream_id}']
        else:
            self.stream_maps = ['-map', '"[ss]"', '-map', '"[dm]"']

    @abstractmethod
    def _set_filter(self) -> List[str]:
        pass

    @abstractmethod
    def _set_encoder(self) -> List[str]:
        pass

    @abstractmethod
    def _set_metadata(self) -> Dict[str, str]:
        pass


@dataclass
class OpusStream(StreamObject):
    # Bitrates from: https://wiki.xiph.org/index.php?title=Opus_Recommended_Settings
    def _set_filter(self):
        filter_dict = {'1': ['-af', 'channelmap=channel_layout=mono"'],
                       '2': ['-af', 'channelmap=channel_layout=stereo'],
                       '4': ['-ac', '2'],
                       '6': ['-filter_complex', f'"[a:{self.stream_id}]'
                                                f'|pan=stereo'
                                                f'|c0=.9*FL+1.10*FC+.4*BL'
                                                f'|c1=.9*FR+1.10*FC+.4*BR'
                                                f'[dm];'
                                                f'[a:{self.stream_id}'
                                                f']channelmap=channel_layout=5.1'
                                                f'[ss]"'],
                       '8': ['-filter_complex', f'"[a:{self.stream_id}]'
                                                f'|pan=stereo'
                                                f'|c0=.9*FL+1.10*FC+.4*BL'
                                                f'|c1=.9*FR+1.10*FC+.4*BR'
                                                f'[dm];'
                                                f'[a:{self.stream_id}'
                                                f']channelmap=channel_layout=7.1'
                                                f'[ss]"']}

        self.filter_flags = filter_dict[self.channel_num]

    def _set_encoder(self):
        encoder_dict = {'1': ['-c:a', 'libopus', '-b:a', '96k'],
                        '2': ['-c:a', 'libopus', '-b:a', '128k'],
                        '4': ['-c:a', 'libopus', '-b:a', '128k'],
                        '6': ['-c:a', 'libopus', '-b:a:0', '256k', '-b:a:1', '128k'],
                        '8': ['-c:a', 'libopus', '-b:a:0', '450k', '-b:a:1', '128k']}

        self.encoder_flags = encoder_dict[self.channel_num]

    def _set_metadata(self):
        metadata_dict = {'1': ['-metadata:s:a:0', f'title="{lang_dict[self.stream_lang]} '
                                                  '- Mono - Opus - 96kbps"',
                               '-metadata:s:a:0', f'language={self.stream_lang}'],
                         '2': ['-metadata:s:a:0', f'title="{lang_dict[self.stream_lang]} '
                                                  '- Stereo - Opus - 128kbps"',
                               '-metadata:s:a:0', f'language={self.stream_lang}'],
                         '4': ['-metadata:s:a:0', f'title="{lang_dict[self.stream_lang]} '
                                                  '- Stereo - Opus - 128kbps"',
                               '-metadata:s:a:0', f'language={self.stream_lang}'],
                         '6': ['-metadata:s:a:0', f'title="{lang_dict[self.stream_lang]} '
                                                  '- Surround Sound - 5.1 - Opus - 256kbps"',
                               '-metadata:s:a:0', f'language={self.stream_lang}',
                               '-metadata:s:a:1', f'title="{lang_dict[self.stream_lang]} '
                                                   '- Stereo Downmix - Opus - 128kbps"',
                               '-metadata:s:a:1', f'language={self.stream_lang}'],
                         '8': ['-metadata:s:a:0', f'title="{lang_dict[self.stream_lang]} '
                                                  '- Surround Sound - 7.1 - Opus - 450kbps"',
                               '-metadata:s:a:0', f'language={self.stream_lang}',
                               '-metadata:s:a:1', f'title="{lang_dict[self.stream_lang]} '
                                                   '- Stereo Downmix - Opus - 128kbps"',
                               '-metadata:s:a:1', f'language={self.stream_lang}']}

        self.metadata = metadata_dict[self.channel_num]
