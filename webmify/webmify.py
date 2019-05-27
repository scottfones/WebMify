#!/usr/bin/env python

import re
import sys
import tmdb_lookup
import input_parser
import encode_object

from pathlib import Path
from optparse import OptionParser, OptionGroup


def main():
    parser = OptionParser(usage='%prog <input files, can batch using *> [options]')

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
                           help='number of cpu threads, default = 16')

    parser.add_option_group(ffmpeg_opts)

    tmdb_opts = OptionGroup(parser,
                            'The Movie Database Options',
                            'These options modify TMDb search and metadata.')

    tmdb_opts.add_option('--episode',
                         action='store', type='string', dest='episode_num',
                         default='',
                         help='tv series episode number')

    tmdb_opts.add_option('--season',
                         action='store', type='string', dest='season_num',
                         default='',
                         help='tv series season number')

    tmdb_opts.add_option('-t', '--title',
                         action='store', type='string', dest='media_title',
                         default='',
                         help='movie or series title, default = file base')

    parser.add_option_group(tmdb_opts)

    parser.add_option('--delete',
                      action='store_true', dest='del_orig',
                      default=False,
                      help='delete original file, default = false')

    parser.add_option('--dvd-order',
                      action='store_true', dest='dvd_order',
                      default=False,
                      help='prefer dvd episode order, default = false')

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
                      help='perform test run for matching and encode settings')

    (options, args) = parser.parse_args()

    print(f'{args}')
    work_list = [Path(file) for file in args]

    repeat_title = ''
    for file in work_list:
        print('\nX        NEW ENCODE        X\n')

        if input_parser.is_movie(file):
            encode = encode_object.MovieObject(file,
                                               title=options.media_title,
                                               out_file=options.out_filename,
                                               post_delete=options.del_orig)
        else:
            encode = encode_object.TVObject(file,
                                             title=options.media_title,
                                             season_num=options.season_num,
                                             episode_num=options.episode_num,
                                             out_file=options.out_filename,
                                             post_delete=options.del_orig)

        """
        encode = encode_object.EncodeObject(file)

        # Construct Title and Episode Information
        if options.media_title == '':
            encode.title = input_parser.get_title(file.name)
        else:
            encode.title = options.media_title

        if options.tv_season_num == '':
            encode.season_num = input_parser.get_season(file.name)
        else:
            encode.title_num = options.tv_season_num

        if options.tv_episode_num == '':
            encode.episode_num = input_parser.get_episode(file.name)
        else:
            encode.episode_num = options.tv_episode_num

        # Look-up Movie or Episode Information
        # skip title look-up if file base matches previous loop
        if repeat_title == encode.title:
            tmdb_info[1] = tmdb_lookup.find_tv_episode(tmdb_info[0],
                                                       encode.season_num,
                                                       encode.episode_num)
            tmdb_lookup.display_tv_episode(tmdb_info[0],
                                           tmdb_info[1])
        else:
            tmdb_info = tmdb_lookup.look_up(encode.title,
                                            encode.season_num,
                                            encode.episode_num)

        encode.overview = tmdb
        encode.metadata = tmdb_lookup.get_tv_metadata(tmdb_info[0], tmdb_info[1])

        # Next Iteration Update
        repeat_title = encode.title
        """

        print(encode)

if __name__ == '__main__':
    main()
