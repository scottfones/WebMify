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
    file_summary: str
    wrap_cmd: List[str] = field(default_factory=list)

    denoise: bool = False

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
class ChromecastWrapper(WrapperObject):
    video_stream: encode_object.ChromecastEncode = None
    audio_stream: encode_object.AACNormalizedDownmixEncode = None

    def __post_init__(self):
        super().__post_init__()

        self.out_file = self.in_file.with_suffix('.chromecast.mp4')
        self.video_stream = encode_object.ChromecastEncode(in_file=self.in_file,
                                                           out_file=self.out_file)
        self.audio_stream = encode_object.AACNormalizedDownmixEncode(in_file=self.in_file,
                                                                     out_file=self.out_file)

        self.wrap()

    def wrap(self):
        self.wrap_cmd = [settings.ffmpeg_bin,
                         '-i', self.video_stream.out_file,
                         '-i', self.audio_stream.out_file,
                         '-map', '0:0', '-map', '1:0',
                         '-c:v', 'copy', '-c:a', 'copy',
                         '-metadata', f'title={self.file_title} - Streaming Version',
                         '-metadata', f'summary={self.file_summary}',
                         '-movflags', '+faststart', self.out_file]

        print('\n\nRunning: Chromecast Wrapper')
        print(f"Command: {' '.join(str(element) for element in self.wrap_cmd)}\n")
        self.comp_proc = subprocess.run(self.wrap_cmd)

        print('\n\nClean-up:')
        print(f'Deleting video file: {self.video_stream.out_file}')
        self.video_stream.out_file.unlink()
        print(f'Deleting audio file: {self.audio_stream.out_file}')
        self.audio_stream.out_file.unlink()


@dataclass
class TVWrapper(WrapperObject, ABC):
    video_stream: encode_object.VP9Encode = None
    audio_stream: encode_object.OpusEncode = None

    def __post_init__(self):
        super().__post_init__()

        self.out_file = self.in_file.with_suffix('.webm')
        self.video_stream = encode_object.VP9Encode(in_file=self.in_file,
                                                    out_file=self.out_file)
        self.audio_stream = encode_object.OpusEncode(in_file=self.in_file,
                                                     out_file=self.out_file)

@dataclass
class TVMultiChannelWrapper(TVWrapper):
    downmix_stream: encode_object.OpusNormalizedDownmixEncode = None

    def __post_init__(self):
        super().__post_init__()

        self.downmix_stream = encode_object.OpusNormalizedDownmixEncode(in_file=self.in_file, out_file=self.out_file)

        self.wrap()

    def wrap(self):
        self.wrap_cmd = [settings.ffmpeg_bin,
                         '-i', self.video_stream.out_file,
                         '-i', self.audio_stream.out_file,
                         '-i', self.downmix_stream.out_file,
                         '-map', '0:0', '-map', '1:0', '-map', '2:0'
                         '-c:v', 'copy', '-c:a', 'copy',
                         '-metadata', f'title={self.file_title}',
                         '-metadata', f'summary={self.file_summary}',
                         self.out_file]

        print('\n\nRunning: TV - Surround Wrapper')
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
class TVMultiChannelSubtitleWrapper(TVWrapper):
    downmix_stream: encode_object.OpusNormalizedDownmixEncode = None
    sub_stream: encode_object.WebVTTEncode = None

    def __post_init__(self):
        super().__post_init__()

        self.downmix_stream = encode_object.OpusNormalizedDownmixEncode(in_file=self.in_file, 
                                                                        out_file=self.out_file)
        self.sub_stream = encode_object.WebVTTEncode(in_file=self.in_file, 
                                                     out_file=self.out_file)

        self.wrap()

    def wrap(self):
        self.wrap_cmd = [settings.ffmpeg_bin,
                         '-i', self.video_stream.out_file,
                         '-i', self.audio_stream.out_file,
                         '-i', self.downmix_stream.out_file,
                         '-i', self.sub_stream.out_file,
                         '-map', '0:0', '-map', '1:0',
                         '-map', '2:0', '-map', '3:0',
                         '-c:v', 'copy', '-c:a', 'copy', '-c:s', 'copy'
                         '-metadata', f'title={self.file_title}',
                         '-metadata', f'summary={self.file_summary}',
                         self.out_file]

        print('\n\nRunning: TV - Surround - Subtitles Wrapper')
        print(f"Command: {' '.join(str(element) for element in self.wrap_cmd)}\n")
        self.comp_proc = subprocess.run(self.wrap_cmd)

        print('\n\nClean-up:')
        print(f'Deleting video file: {self.video_stream.out_file}')
        self.video_stream.out_file.unlink()
        print(f'Deleting surround file: {self.audio_stream.out_file}')
        self.audio_stream.out_file.unlink()
        print(f'Deleting downmix file: {self.downmix_stream.out_file}')
        self.downmix_stream.out_file.unlink()
        print(f'Deleting subtitle file: {self.sub_stream.out_file}')
        self.sub_stream.out_file.unlink()


@dataclass
class TVStereoWrapper(TVWrapper):
    def __post_init__(self):
        super().__post_init__()

        self.wrap()

    def wrap(self):
        self.wrap_cmd = [settings.ffmpeg_bin,
                         '-i', self.video_stream.out_file,
                         '-i', self.audio_stream.out_file,
                         '-map', '0:0', '-map', '1:0',
                         '-c:v', 'copy', '-c:a', 'copy',
                         '-metadata', f'title={self.file_title}',
                         '-metadata', f'summary={self.file_summary}',
                         self.out_file]

        print('\n\nRunning: TV - Stereo Wrapper')
        print(f"Command: {' '.join(str(element) for element in self.wrap_cmd)}\n")
        self.comp_proc = subprocess.run(self.wrap_cmd)

        print('\n\nClean-up:')
        print(f'Deleting video file: {self.video_stream.out_file}')
        self.video_stream.out_file.unlink()
        print(f'Deleting audio file: {self.audio_stream.out_file}')
        self.audio_stream.out_file.unlink()


@dataclass
class TVStereoSubsWrapper(TVWrapper):
    sub_stream: encode_object.WebVTTEncode = None

    def __post_init__(self):
        super().__post_init__()

        self.sub_stream = encode_object.WebVTTEncode(in_file=self.in_file, out_file=self.out_file)

        self.wrap()

    def wrap(self):
        self.wrap_cmd = [settings.ffmpeg_bin,
                         '-i', self.video_stream.out_file,
                         '-i', self.audio_stream.out_file,
                         '-i', self.sub_stream.out_file,
                         '-map', '0:0', '-map', '1:0', '-map', '2:0',
                         '-c:v', 'copy', '-c:a', 'copy', '-c:s', 'copy',
                         '-metadata', f'title={self.file_title}',
                         '-metadata', f'summary={self.file_summary}',
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
