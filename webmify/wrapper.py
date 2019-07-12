import settings
import encode_object

import subprocess
from pathlib import Path, PurePath
from typing import List, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class WrapperObject(ABC):
    """Abstract Wrapper for accumulating and
    constructing mkvmerge parameters.
    """

    in_file: PurePath
    out_file: PurePath
    file_title: str
    wrap_cmd: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.in_file, PurePath):
            self.in_file = Path(self.in_file)

        if not self.out_file:
            self.out_file = Path('.') / (self.in_file.stem + '.out.mkv')

        if not isinstance(self.out_file, PurePath):
            self.out_file = Path(self.out_file)

    @abstractmethod
    def wrap(self) -> None:
        pass


@dataclass
class TVWrapper(WrapperObject, ABC):
    ep_info: str = ''

    video_stream: encode_object.VP9Encode = None
    audio_stream: encode_object.OpusEncode = None

    def __post_init__(self):
        super().__post_init__()

        self.out_file = self.in_file.with_suffix('.webm')
        self.video_stream = encode_object.VP9Encode(in_file=self.in_file, out_file=self.out_file)
        self.audio_stream = encode_object.OpusEncode(in_file=self.in_file, out_file=self.out_file)

@dataclass
class TVMultiChannelWrapper(TVWrapper):
    downmix_stream: encode_object.OpusNormalizedDownmixEncode = None

    def __post_init__(self):
        super().__post_init__()

        self.downmix_stream = encode_object.OpusNormalizedDownmixEncode(in_file=self.in_file, out_file=self.out_file)

        self.wrap()

    def wrap(self):
        self.wrap_cmd = ['mkvmerge', '-o', self.out_file,
                         '--title', self.file_title,
                         '--track-order', '0:0,1:0,2:0',
                         '--track-name', f'0:{self.video_stream.stream.metadata[1][7:-1]}',
                         self.video_stream.out_file,
                         '--track-name', f'0:{self.audio_stream.stream.metadata[1][7:-1]}',
                         '--no-chapters', self.audio_stream.out_file,
                         '--track-name', f'0:{self.downmix_stream.stream.metadata[1][7:-1]}',
                         '--no-chapters', self.downmix_stream.out_file]

        print('\n\nRunning: TV - Surround Audio Wrapper')
        print(f"Command: {' '.join(str(element) for element in self.wrap_cmd)}\n")
        self.comp_proc = subprocess.run(self.wrap_cmd)

        print('\n\nClean-up:')
        print(f'Deleting video file: {self.video_stream.out_file}')
        self.video_stream.out_file.unlink()
        print(f'Deleting surround file: {self.audio_stream.out_file}')
        self.audio_stream.out_file.unlink()
        print(f'Deleting downmix file: {self.downmix_stream.out_file}')
        self.downmix_stream.out_file.unlink()


@dataclass
class TVStereoSubsWrapper(TVWrapper):
    sub_stream: encode_object.WebVTTEncode = None

    def __post_init__(self):
        super().__post_init__()

        self.sub_stream = encode_object.WebVTTEncode(in_file=self.in_file, out_file=self.out_file)

        self.wrap()

    def wrap(self):
        """
        self.wrap_cmd = ['mkvmerge', '-o', self.out_file,
                         '--title', self.file_title,
                         '--track-order', '0:0,1:0,2:0',
                         '--track-name', f'0:{self.video_stream.stream.metadata[1][7:-1]}',
                         self.video_stream.out_file,
                         '--track-name', f'0:{self.audio_stream.stream.metadata[1][7:-1]}',
                         '--no-chapters', self.audio_stream.out_file,
                         '--track-name', f'0:{self.sub_stream.stream.metadata[1][7:-1]}',
                         '--no-chapters', self.sub_stream.out_file]
        """
        self.wrap_cmd = [settings.ffmpeg_bin,
                         '-i', self.video_stream.out_file,
                         '-i', self.audio_stream.out_file,
                         '-i', self.sub_stream.out_file,
                         '-map', '0:0', '-map', '1:0', '-map', '2:0',
                         '-c:v', 'copy', '-c:a', 'copy', '-c:s', 'copy',
                         '-metadata', f'title={self.file_title}',
                         '-metadata', f'summary={self.ep_info}',
                         self.out_file]

        print('\n\nRunning: TV - Stereo - Subtitles Wrapper')
        print(f"Command: {' '.join(str(element) for element in self.wrap_cmd)}\n")
        self.comp_proc = subprocess.run(self.wrap_cmd)

        print('\n\nClean-up:')
        print(f'Deleting video file: {self.video_stream.out_file}')
        self.video_stream.out_file.unlink()
        print(f'Deleting audio file: {self.audio_stream.out_file}')
        self.audio_stream.out_file.unlink()
        print(f'Deleting subtitle file: {self.sub_stream.out_file}')
        self.sub_stream.out_file.unlink()
