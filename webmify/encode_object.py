import input_parser
import tmdb_lookup
import thetvdb_lookup

from pathlib import Path
from typing import List, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class EncodeObject(ABC):
    """Abstract Class for accumulating and
    constructing encoding parameters.
    """

    in_file: str = ''
    title: str = ''
    air_date: str = ''
    overview: str = ''
    v_codec: str = ''
    a_codec: str = ''
    hdr: bool = False
    v_filters: List[str] = field(default_factory=list)
    a_filters: List[str] = field(default_factory=list)
    media_maps: List[str] = field(default_factory=list)
    v_encode: List[str] = field(default_factory=list)
    a_encode: List[str] = field(default_factory=list)
    out_file: str = ''
    post_delete: bool = False
    delete_list: List[str] = field(default_factory=list)


@dataclass
class MovieObject(EncodeObject):
    """Movie specific EncodeObject class"""
    v_codec: str = 'x264'
    a_codec: str = 'aac'

    def __post_init__(self):
        if not self.title:
            self.title = input_parser.get_title(self.in_file)

        self.title, self.air_date, self.overview = tmdb_lookup.get_movie_info(self.title)


@dataclass
class TVObject(EncodeObject):
    """TV Specific Encode Object Class"""
    s_num: str = ''
    ep_num: str = ''
    ep_title: str = ''

    v_codec: str = 'vp9'
    a_codec: str = 'opus'

    def __post_init__(self):
        if not self.title:
            self.title = input_parser.get_title(self.in_file)

        if not self.s_num:
            self.s_num = input_parser.get_season(self.in_file)

        if not self.ep_num:
            self.ep_num = input_parser.get_episode(self.in_file)

        if self.prev_job:
            self.cur_base = input_parser.get_title(self.in_file)
            self.prev_base = input_parser.get_title(self.prev_job.in_file)

        if self.prev_job and self.prev_base == self.cur_base:
            self.title = self.prev_job.title
        else:
            self.title = thetvdb_lookup.get_tv_title(self.title)

        self.ep_title, self.overview, self.air_date = thetvdb_lookup.get_tv_info(self.title,
                                                                                 self.s_num,
                                                                                 self.ep_num)

