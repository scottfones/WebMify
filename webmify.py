#!/usr/bin/env python

import re
import subprocess
import tmdb_lookup

from pathlib import Path
from collections import Counter
from optparse import OptionParser, OptionGroup


def main():
    parser = OptionParser(usage='%prog <input file, batch using *> [options]')

    ffmpeg_opts = OptionGroup(parser,
                              'Encoding Options',
                              'These options modify ffmpeg encoding.')

    ffmpeg_opts.add_option('--burn-subs',
                           action='store_true', dest='burn_subs',
                           default=False,
                           help='burn subtitles into video, default = false')

    ffmpeg_opts.add_option('--denoise',
                           action='store_true', dest='denoise',
                           default=False,
                           help='Apply fftdnoiz filter, default = false')

    ffmpeg_opts.add_option('--external-subs',
                           action='store_true', dest='ext_subs',
                           default=False,
                           help='include external subtitles with shared base name, srt format')

    ffmpeg_opts.add_option('--no-subs',
                           action='store_true', dest='no_subs',
                           default=False,
                           help='bypass search and encoding of subtitles')

    ffmpeg_opts.add_option('-q', '--quality', '--crf',
                           action='store', type='string', dest='crf',
                           default='20',
                           help='set encoding quality, default = 20')

    ffmpeg_opts.add_option('--threads',
                           action='store', type='string', dest='thread_count',
                           default='16',
                           help='number of cpu threads to assign, default = 16')

    parser.add_option_group(ffmpeg_opts)

    tmdb_opts = OptionGroup(parser,
                            'The Movie Database Options',
                            'These options modify TMDb search and metadata.')

    tmdb_opts.add_option('--episode',
                         action='store', type='string', dest='tv_episode_num',
                         default='',
                         help='tv series episode number')

    tmdb_opts.add_option('--season',
                         action='store', type='string', dest='tv_season_num',
                         default='',
                         help='tv series season number')

    tmdb_opts.add_option('-t', '--title',
                         action='store', type='string', dest='media_title',
                         default='',
                         help='movie or series title, default = file base name')

    parser.add_option_group(tmdb_opts)

    parser.add_option('--delete',
                      action='store_true', dest='del_orig',
                      default=False,
                      help='delete original file after encode, default = false')

    parser.add_option('--dvd-order',
                      action='store_true', dest='dvd_order',
                      default=False,
                      help='episode look-up based on dvd order, default = false')

    parser.add_option('-f', '--filename', '--file',
                      action='store', type='string', dest='out_filename',
                      default='',
                      help='output base filename, default = file base name')

    parser.add_option('-m', '--match',
                      action='store', type='string', dest='file_pattern',
                      default='*.mkv',
                      help='pattern to match, default = *.mkv')

    parser.add_option('-o', '--output', '--out',
                      action='store', type='string', dest='out_path',
                      default='./',
                      help='path to the output folder, default = ./')

    parser.add_option('--test',
                      action='store_true', dest='test_run_bool',
                      default=False,
                      help='perform trial run to test matching and encode settings')

    (options, args) = parser.parse_args()

    raw_input = args[0]



    tmdb_info = tmdb_lookup.look_up(options.media_title,
                                    options.tv_season_num,
                                    options.tv_episode_num)

    print(f'Return: {tmdb_info}')

if __name__ == '__main__':
    main()
