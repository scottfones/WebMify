import input_parser
import tmdb_lookup
import thetvdb_lookup

from pathlib import Path
from typing import List, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
# from abc import ABCMeta, abstractmethod


@dataclass
class EncodeObject(ABC):
    """Class for accumulating and constructing encoding parameters."""

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

    def _ready_check(self) -> Tuple[bool, str]:
        """Check for non-default values in all required variables.

        Return False if any required values are missing.
        """

        if not self.in_file:
            return (False, 'in_file')
        elif not self.media_maps:
            return (False, 'media_maps')
        elif not self.v_encode:
            return (False, 'v_encode')
        elif not self.a_encode:
            return (False, 'a_encode')
        elif not self.out_file:
            return (False, 'out_file')
        else:
            return (True, '0')

@dataclass
class MovieObject(EncodeObject):
    v_codec: str = 'x264'
    a_codec: str = 'aac'

    def __post_init__(self):
        if not self.title:
            self.title = input_parser.get_title(self.in_file)

        self.title, self.air_date, self.overview = tmdb_lookup.get_movie_info(self.title)

@dataclass
class TVObject(EncodeObject):
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

        self.title = thetvdb_lookup.get_tv_title(self.title)

        self.ep_title, self.overview, self.air_date = thetvdb_lookup.get_tv_info(self.title,
                                                                                 self.s_num,
                                                                                 self.ep_num)
