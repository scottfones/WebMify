import unittest

from pathlib import Path
from webmify import input_parser


titles = ['/home/test/title1.mkv',
          'c:/Program Files/title2.mkv',
          'movie.mp4',
          'film3.m4v',
          'tvShow.s01e48.mkv',
          'program.S7E11.webm',
          'series.s00E3.mp4',
          'show.S100e00']


class TestInputParser(unittest.TestCase):
    """Testing class for input_parser.py"""

    def test_get_title(self):
        answrs = ['title1',
                  'title2',
                  'movie',
                  'film3',
                  'tvShow',
                  'program',
                  'series',
                  'show']

        for test_title, test_aswr in zip(titles, answrs):
            test_resp = input_parser.get_title(test_title)
            self.assertEqual(test_resp, test_aswr)

            test_resp = input_parser.get_title(Path(test_title))
            self.assertEqual(test_resp, test_aswr)

    def test_get_season(self):
        answrs = ['',
                  '',
                  '',
                  '',
                  '01',
                  '07',
                  '00',
                  '100']

        for test_title, test_aswr in zip(titles, answrs):
            test_resp = input_parser.get_season(test_title)
            self.assertEqual(test_resp, test_aswr)

            test_resp = input_parser.get_season(Path(test_title))
            self.assertEqual(test_resp, test_aswr)

    def test_get_episode(self):
        answrs = ['',
                  '',
                  '',
                  '',
                  '48',
                  '11',
                  '03',
                  '00']

        for test_title, test_aswr in zip(titles, answrs):
            test_resp = input_parser.get_episode(test_title)
            self.assertEqual(test_resp, test_aswr)

            test_resp = input_parser.get_episode(Path(test_title))
            self.assertEqual(test_resp, test_aswr)

    def test_is_movie(self):
        answrs = [True,
                  True,
                  True,
                  True,
                  False,
                  False,
                  False,
                  False]

        for test_title, test_aswr in zip(titles, answrs):
            test_resp = input_parser.is_movie(test_title)
            self.assertEqual(test_resp, test_aswr)

            test_resp = input_parser.is_movie(Path(test_title))
            self.assertEqual(test_resp, test_aswr)
