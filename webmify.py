#!/usr/bin/env python

import re
import subprocess
import tmdb_lookup

from pathlib import Path
from collections import Counter
from optparse import OptionParser


def main():
    parser = OptionParser()

    parser.add_option('--burn-subs',
                      action='store_true', dest='burn_subs',
                      default=False,
                      help='must be used in combination with --no-subs, default = false')

    parser.add_option('--delete',
                      action='store_true', dest='del_orig',
                      default=False,
                      help='delete original file after encode, default = false')

    parser.add_option('--denoise',
                      action='store_true', dest='denoise',
                      default=False,
                      help='Apply light fftdnoiz filter, default = false')

    parser.add_option('--dvd-order',
                      action='store_true', dest='dvd_order',
                      default=False,
                      help='episode look-up based on dvd order, default = false')

    parser.add_option('--episode',
                      action='store', type='string', dest='tv_episode_num',
                      default='',
                      help='tv series episode number')

    parser.add_option('--external-subs',
                      action='store_true', dest='ext_subs',
                      default=False,
                      help='look for external subtitles with shared base name, srt format')

    parser.add_option('-f', '--filename', '--file',
                      action='store', type='string', dest='out_filename',
                      default='',
                      help='output base filename, default = file base name')

    parser.add_option('-i', '--input', '--in',
                      action='store', type='string', dest='in_path',
                      default='./',
                      help='path to the input folder, default = ./')

    parser.add_option('--interactive',
                      action='store_true', dest='active_choice',
                      default=False,
                      help='interactively select the correct show on look-up, default = false')

    parser.add_option('-m', '--match',
                      action='store', type='string', dest='file_pattern',
                      default='*.mkv',
                      help='pattern to match, default = *.mkv')

    parser.add_option('--media-type',
                      action='store', type='string', dest='media_type',
                      default='tv',
                      help='specify tv or movie for metadata look-up, default = tv')

    parser.add_option('--no-subs',
                      action='store_true', dest='no_subs',
                      default=False,
                      help='bypass check and encoding of subtitles')

    parser.add_option('-o', '--output', '--out',
                      action='store', type='string', dest='out_path',
                      default='./',
                      help='path to the output folder, default = ./')

    parser.add_option('-q', '--quality', '--crf',
                      action='store', type='string', dest='crf',
                      default='20',
                      help='encode quality, default = 20')

    parser.add_option('--season',
                      action='store', type='string', dest='tv_season_num',
                      default='',
                      help='tv series season number')

    parser.add_option('--test',
                      action='store_true', dest='test_run_bool',
                      default=False,
                      help='perform trial run to test matching and encode settings')

    parser.add_option('--threads',
                      action='store', type='string', dest='thread_count',
                      default='16',
                      help='number of cpu threads to assign, default = 16')

    parser.add_option('-t', '--title',
                      action='store', type='string', dest='media_title',
                      default='',
                      help='movie or series title for themoviedb metadata, default = file base name')

    (options, args) = parser.parse_args()

    if options.media_type.lower() == 'tv':
        tmdb_info = tmdb_lookup.look_up(options.media_title,
                                        options.tv_season_num, 
                                        options.tv_episode_num)
    else:
        tmdb_info = tmdb_lookup.look_up(options.media_title)

if __name__ == '__main__':
    main()
