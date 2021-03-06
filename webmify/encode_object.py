import settings
import stream_object
import stream_helpers

import re
import subprocess
from pathlib import Path, PurePath
from typing import List, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

ffmpeg_bin = settings.ffmpeg_bin


@dataclass
class EncodeObject(ABC):
    """Abstract Class for accumulating and
    constructing encoding parameters.
    """

    in_file: PurePath
    out_file: PurePath = ''
    stream: stream_object.StreamObject = None
    stream_id: str = '0'
    work_title: str = ''
    encode_cmd: List[str] = field(default_factory=list)
    encode_capture: bool = False

    def __post_init__(self):
        if not isinstance(self.in_file, PurePath):
            self.in_file = Path(self.in_file)

        if not self.out_file:
            self.out_file = Path('.') / (self.in_file.stem + '.out.mkv')

        if not isinstance(self.out_file, PurePath):
            self.out_file = Path(self.out_file)

        self._set_stream()
        self._do_encode()
        self._clean_up()

    @abstractmethod
    def _set_stream(self):
        pass

    def _do_encode(self) -> None:
        self.encode_cmd = [f'{ffmpeg_bin}', '-i', f'{self.in_file}']
        if self.stream.filter_flags:
            self.encode_cmd += self.stream.filter_flags
        if self.stream.stream_maps:
            self.encode_cmd += self.stream.stream_maps
        if self.stream.encoder_flags:
            self.encode_cmd += self.stream.encoder_flags
        if self.stream.metadata:
            self.encode_cmd += self.stream.metadata
        self.encode_cmd += [f'{self.out_file}']

        print(f'\n\nRunning: {self.work_title} Encode')
        print(f"Command: {' '.join(str(element) for element in self.encode_cmd)}\n")
        self.comp_proc = subprocess.run(self.encode_cmd,
                                        capture_output=self.encode_capture,
                                        text=True)

    def _clean_up(self) -> None:
        pass


@dataclass
class AACNormalizedDownmixEncode(EncodeObject):
    def _set_stream(self):
        self.norm_second_encode = NormalizeSecondPassEncode(in_file=self.in_file,
                                                            out_file=self.out_file,
                                                            stream_id=self.stream_id)

        self.work_title = 'AAC Normalized Downmix'
        self.in_file = self.norm_second_encode.out_file
        self.out_file = self.out_file.with_suffix('.norm.aac.mkv')
        self.stream = stream_object.AACNormalizedDownmixStream(in_file=self.in_file,
                                                               stream_id='0')

    def _clean_up(self):
        if self.norm_second_encode.out_file.exists():
            self.norm_second_encode.out_file.unlink()


@dataclass
class NormalizeFirstPassEncode(EncodeObject):
    def _set_stream(self):
        self.stream_channels = stream_helpers.get_audio_ch(self.in_file, self.stream_id)
        if int(self.stream_channels) > 2:
            self.downmix_encode = StereoDownmixEncode(in_file=self.in_file,
                                                      out_file=self.out_file,
                                                      stream_id=self.stream_id)
            self.in_file = self.downmix_encode.out_file

        self.encode_capture = True
        self.work_title = 'Normalization First Pass'
        self.stream = stream_object.NormalizedFirstPassStream(self.in_file,
                                                              self.stream_id)

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

    def _clean_up(self):
        self._get_norm_i()
        self._get_norm_tp()
        self._get_norm_lra()
        self._get_norm_thresh()
        self._get_norm_offset()


@dataclass
class NormalizeSecondPassEncode(EncodeObject):
    def _set_stream(self):
        self.norm_first_encode = NormalizeFirstPassEncode(in_file=self.in_file,
                                                          out_file=self.out_file,
                                                          stream_id=self.stream_id)

        self.work_title = 'Normalization Second Pass'
        self.in_file = self.norm_first_encode.in_file
        self.out_file = self.out_file.with_suffix('.norm.mkv')
        self.stream = stream_object.NormalizedSecondPassStream(self.norm_first_encode.in_file,
                                                               self.stream_id,
                                                               norm_i=self.norm_first_encode.norm_i,
                                                               norm_tp=self.norm_first_encode.norm_tp,
                                                               norm_lra=self.norm_first_encode.norm_lra,
                                                               norm_thresh=self.norm_first_encode.norm_thresh,
                                                               norm_tar_off=self.norm_first_encode.norm_offset)

    def _clean_up(self):
        try:
            self.norm_first_encode.downmix_encode.out_file.unlink()
        except:
            pass

        self.cur_lra = self.norm_first_encode.out_lra
        if float(self.cur_lra) > 17.0:
            self.old_name = self.out_file.with_suffix('.old.mkv')
            self.out_file.rename(self.old_name)

            NormalizeSecondPassEncode(in_file=self.old_name,
                                      out_file=self.out_file.parent / self.out_file.stem,
                                      stream_id=self.stream_id)

            if self.old_name.exists():
                self.old_name.unlink()


@dataclass
class OpusEncode(EncodeObject):
    def _set_stream(self):
        self.work_title = 'Opus'
        self.out_file = self.out_file.with_suffix('.audio.opus')
        self.stream = stream_object.OpusStream(in_file=self.in_file,
                                               stream_id=self.stream_id)


@dataclass
class OpusNormalizedDownmixEncode(EncodeObject):
    def _set_stream(self):
        self.norm_second_encode = NormalizeSecondPassEncode(in_file=self.in_file,
                                                            out_file=self.out_file,
                                                            stream_id=self.stream_id)

        self.work_title = 'Opus Normalized Downmix'
        self.in_file = self.norm_second_encode.out_file
        self.out_file = self.out_file.with_suffix('.norm.opus')
        self.stream = stream_object.OpusNormalizedDownmixStream(in_file=self.norm_second_encode.out_file,
                                                                stream_id='0')

    def _clean_up(self):
        if self.norm_second_encode.out_file.exists():
            self.norm_second_encode.out_file.unlink()


@dataclass
class StereoDownmixEncode(EncodeObject):
    def _set_stream(self):
        self.work_title = 'Stereo Downmix'
        self.out_file = self.out_file.with_suffix('.downmix.mkv')
        self.stream = stream_object.StereoDownmixStream(self.in_file,
                                                        self.stream_id)


###################################
#                                 #
#        Subtitle Streams         #
#                                 #
###################################


@dataclass
class WebVTTEncode(EncodeObject):
    def _set_stream(self):
        self.work_title = 'Subtitle WebVTT'
        self.out_file = self.out_file.with_suffix('.subs.mkv')
        self.stream = stream_object.WebVTTStream(in_file=self.in_file,
                                                 stream_id=self.stream_id)


###################################
#                                 #
#         Video Streams           #
#                                 #
###################################


@dataclass
class ChromecastEncode(EncodeObject):
    burn_subs: bool = False
    crf: str = '19'
    crop: bool = True
    denoise: bool = False
    sub_file: PurePath = ''

    def _set_stream(self):
        self.work_title = 'Chromecast Video'
        self.out_file = self.out_file.with_suffix('.x264.mkv')
        self.stream = stream_object.ChromecastStream(self.in_file,
                                                     self.stream_id,
                                                     burn_subs=self.burn_subs,
                                                     crf=self.crf,
                                                     crop=self.crop,
                                                     denoise=self.denoise,
                                                     sub_file=self.sub_file)


@dataclass
class VP9Encode(EncodeObject):
    burn_subs: bool = False
    crf: str = '19'
    crop: bool = False
    denoise: bool = False
    sub_file: PurePath = ''

    def _set_stream(self):
        self.out_file = self.out_file.with_suffix('.vp9.webm')
        self.logfile = self.out_file.parent / self.out_file.stem
        self.stream = stream_object.VP9Stream(self.in_file,
                                              self.stream_id,
                                              burn_subs=self.burn_subs,
                                              crf=self.crf,
                                              crop=self.crop,
                                              denoise=self.denoise,
                                              sub_file=self.sub_file)

    def _do_encode(self):
        self.encode_cmd = [f'{ffmpeg_bin}', '-y', '-i', f'{self.in_file}']
        if self.stream.filter_flags:
            self.encode_cmd += self.stream.filter_flags
        self.encode_cmd += self.stream.stream_maps
        self.encode_cmd += self.stream.encoder_flags
        self.encode_cmd += self.stream.metadata
        self.encode_cmd += ['-pass', '1', '-f', 'webm', '-passlogfile',
                            self.logfile, '-strict',
                            'experimental', '/dev/null']

        print('\n\nRunning: VP9 First Pass')
        print(f"Command: {' '.join(str(element) for element in self.encode_cmd)}\n")
        self.comp_proc = subprocess.run(self.encode_cmd)

        self.encode_cmd = [f'{ffmpeg_bin}', '-i', f'{self.in_file}']
        if self.stream.filter_flags:
            self.encode_cmd += self.stream.filter_flags
        self.encode_cmd += self.stream.stream_maps
        self.encode_cmd += self.stream.encoder_flags
        self.encode_cmd += self.stream.metadata
        self.encode_cmd += ['-pass', '2', '-f', 'webm', '-passlogfile',
                            self.logfile, '-strict',
                            'experimental', f'{self.out_file}']

        print('\n\nRunning: VP9 Second Pass')
        print(f"Command: {' '.join(str(element) for element in self.encode_cmd)}\n")
        self.comp_proc = subprocess.run(self.encode_cmd)

    def _clean_up(self):
        self.logfile = self.logfile.parent / (self.logfile.name + f'-{self.stream_id}.log')
        self.logfile.unlink()
