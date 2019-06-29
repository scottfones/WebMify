import stream_object
import stream_helpers

import re
import subprocess
from pathlib import Path, PurePath
from typing import List, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

ffmpeg_bin = 'ffmpeg'


@dataclass
class EncodeObject(ABC):
    """Abstract Class for accumulating and
    constructing encoding parameters.
    """

    in_file: PurePath
    out_file: PurePath = Path('out.mkv')
    encode_cmd: List[str] = field(default_factory=list)

    title: str = ''
    stream_id: str = '0'

    def __post_init__(self):
        if not isinstance(self.in_file, PurePath):
            self.in_file = Path(self.in_file)

        if not isinstance(self.out_file, PurePath):
            self.out_file = Path(self.out_file)

    @abstractmethod
    def do_encode(self) -> None:
        pass


@dataclass
class NormalizeFirstPassEncode(EncodeObject):
    def __post_init__(self):
        super().__post_init__()

        self.stream_channels = stream_helpers.get_audio_ch(self.in_file, self.stream_id)
        if int(self.stream_channels) > 2:
            self.downmix_encode = StereoDownmixEncode(in_file=self.in_file,
                                                      out_file=self.out_file,
                                                      stream_id=self.stream_id)
            self.in_file = self.downmix_encode.out_file

        self.norm_first_stream = stream_object.NormalizedFirstPassStream(self.in_file,
                                                                         self.stream_id)

        self.do_encode()

    def _get_norm_i(self):
        norm_i_re = re.compile('\"input_i\" : \"(.+?)\"')
        self.norm_i = norm_i_re.search(self.comp_proc.stderr).groups()[0]

    def _get_norm_tp(self):
        norm_tp_re = re.compile('\"input_tp\" : \"(.+?)\"')
        self.norm_tp = norm_tp_re.search(self.comp_proc.stderr).groups()[0]

    def _get_norm_lra(self):
        norm_lra_re = re.compile('\"input_lra\" : \"(.+?)\"')
        self.norm_lra = norm_lra_re.search(self.comp_proc.stderr).groups()[0]

        out_lra_re = re.compile('\"output_lra\" : \"(.+?)\"')
        self.out_lra = out_lra_re.search(self.comp_proc.stderr).groups()[0]

    def _get_norm_thresh(self):
        norm_thresh_re = re.compile('\"input_thresh\" : \"(.+?)\"')
        self.norm_thresh = norm_thresh_re.search(self.comp_proc.stderr).groups()[0]

    def _get_norm_offset(self):
        norm_offset_re = re.compile('\"target_offset\" : \"(.+?)\"')
        self.norm_offset = norm_offset_re.search(self.comp_proc.stderr).groups()[0]

    def do_encode(self):
        self.encode_cmd = [f'{ffmpeg_bin}', '-i', f'{self.in_file}']
        self.encode_cmd += self.norm_first_stream.stream_maps
        self.encode_cmd += self.norm_first_stream.filter_flags
        self.encode_cmd += self.norm_first_stream.metadata
        self.encode_cmd.append('-')

        print('\n\nRunning: First Normalization Pass - Please Be Patient')
        print(f"Command: {' '.join(str(element) for element in self.encode_cmd)}\n")
        self.comp_proc = subprocess.run(self.encode_cmd, capture_output=True, text=True)

        self._get_norm_i()
        self._get_norm_tp()
        self._get_norm_lra()
        self._get_norm_thresh()
        self._get_norm_offset()


@dataclass
class NormalizeSecondPassEncode(EncodeObject):
    def __post_init__(self):
        super().__post_init__()

        self.norm_first_encode = NormalizeFirstPassEncode(in_file=self.in_file,
                                                          out_file=self.out_file,
                                                          stream_id=self.stream_id)

        self.norm_second_stream = stream_object.NormalizedSecondPassStream(self.norm_first_encode.in_file,
                                                                           self.stream_id,
                                                                           norm_i=self.norm_first_encode.norm_i,
                                                                           norm_tp=self.norm_first_encode.norm_tp,
                                                                           norm_lra=self.norm_first_encode.norm_lra,
                                                                           norm_thresh=self.norm_first_encode.norm_thresh,
                                                                           norm_tar_off=self.norm_first_encode.norm_offset)

        self.out_file = self.out_file.parent / (self.out_file.stem + '_norm.mkv')

        self.do_encode()

    def do_encode(self):
        self.encode_cmd = [f'{ffmpeg_bin}', '-i', f'{self.norm_first_encode.in_file}']
        self.encode_cmd += self.norm_second_stream.filter_flags
        self.encode_cmd += self.norm_second_stream.encoder_flags
        self.encode_cmd += self.norm_second_stream.metadata
        self.encode_cmd.append(self.out_file)

        print('\n\nRunning: Second Normalization Pass')
        print(f"Command: {' '.join(str(element) for element in self.encode_cmd)}\n")
        self.comp_proc = subprocess.run(self.encode_cmd)


@dataclass
class OpusNormalizedDownmixEncode(EncodeObject):
    def __post_init__(self):
        super().__post_init__()

        self.norm_second_encode = NormalizeSecondPassEncode(in_file=self.in_file,
                                                            out_file=self.out_file,
                                                            stream_id=self.stream_id)

        self.cur_lra = self.norm_second_encode.norm_first_encode.out_lra

        self._work_lra()

        self.out_file = self.out_file.parent / (self.out_file.stem + '_norm.opus')
        self.opus_stream = stream_object.OpusNormalizedDownmixStream(in_file=self.norm_second_encode.out_file,
                                                                     stream_id='0')

        self.do_encode()

    def _work_lra(self):
        self.norm_count = 1

        while float(self.cur_lra) > 18.5:
            self.old_name = self.norm_second_encode.out_file.parent / (self.norm_second_encode.out_file.stem + '_old.mkv')
            self.norm_second_encode.out_file.rename(self.old_name)

            self.norm_second_encode = NormalizeSecondPassEncode(in_file=self.old_name,
                                                                out_file=self.out_file,
                                                                stream_id=self.stream_id)

            self.cur_lra = self.norm_second_encode.norm_first_encode.out_lra
            self.norm_count += 1

            if self.norm_count == 4:
                break

    def do_encode(self):
        self.encode_cmd = [f'{ffmpeg_bin}', '-i', f'{self.norm_second_encode.out_file}']
        self.encode_cmd += self.opus_stream.filter_flags
        self.encode_cmd += self.opus_stream.encoder_flags
        self.encode_cmd += self.opus_stream.metadata
        self.encode_cmd.append(self.out_file)

        print('\n\nRunning: Opus Normalized Downmix Encode')
        print(f"Command: {' '.join(str(element) for element in self.encode_cmd)}\n")
        self.comp_proc = subprocess.run(self.encode_cmd)


@dataclass
class StereoDownmixEncode(EncodeObject):
    def __post_init__(self):
        super().__post_init__()

        self.out_file = self.out_file.parent / (self.out_file.stem + '_downmix.mkv')

        self.down_stream = stream_object.StereoDownmixStream(self.in_file,
                                                             self.stream_id)

        self.do_encode()

    def do_encode(self):
        self.encode_cmd = [f'{ffmpeg_bin}', '-i', f'{self.in_file}']
        self.encode_cmd += self.down_stream.filter_flags
        self.encode_cmd += self.down_stream.stream_maps
        self.encode_cmd += self.down_stream.encoder_flags
        self.encode_cmd += self.down_stream.metadata
        self.encode_cmd.append(self.out_file)

        print('\n\nRunning: Stereo Downmix')
        print(f"Command: {' '.join(str(element) for element in self.encode_cmd)}\n")
        self.comp_proc = subprocess.run(self.encode_cmd)
