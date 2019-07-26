#!/usr/bin/python3
import tmdb_lookup
import input_parser
import stream_helpers
import thetvdb_lookup
import wrapper

import re
import sys
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

    ffmpeg_opts.add_option('--crop',
                           action='store_true', dest='crop',
                           default=False,
                           help='apply crop, default = false')

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
                           default='19',
                           help='set encoding quality, default = 19')

    ffmpeg_opts.add_option('--sub-id',
                           action='store', type='string', dest='sub_id',
                           default='0',
                           help='relative subtitle stream number, default = 0')

    ffmpeg_opts.add_option('--threads',
                           action='store', type='string', dest='thread_count',
                           default='16',
                           help='number of cpu threads, default = 16')

    parser.add_option_group(ffmpeg_opts)

    tmdb_opts = OptionGroup(parser,
                            'Metadata Options',
                            'These options modify TMDb and '
                            'TheTVDatabase search and metadata.')

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

    parser.add_option('-o', '--output', '--out',
                      action='store', type='string', dest='out_file',
                      default='',
                      help='output filename')

    parser.add_option('--test',
                      action='store_true', dest='test_run_bool',
                      default=False,
                      help='perform test run for matching and encode settings')

    (options, args) = parser.parse_args()

    work_list = [Path(file) for file in args]

    orig_out_file = options.out_file
    prev_file = None
    for file in work_list:
        print('\n\nX        NEW ENCODE        X\n\n')

        if options.ext_subs:
            sub_file = file.with_suffix('.srt')
        elif options.no_subs:
            sub_file = ''
        elif (stream_helpers.get_sub_stream(file)
              and stream_helpers.get_sub_type(file, options.sub_id) != 'hdmv_pgs_subtitle'):
            sub_file = file
        else:
            sub_file = ''

        if not input_parser.is_batch_repeat(prev_file, file):
            if not options.media_title:
                title = input_parser.get_title(file)
            else:
                title = options.media_title

        if input_parser.is_movie(file):
            file_title, file_summary = tmdb_lookup.get_movie_info(title)

            wrapper.ChromecastWrapper(in_file=file,
                                      out_file=options.out_file,
                                      file_title=file_title,
                                      file_summary=file_summary,
                                      crf=options.crf,
                                      crop=options.crop,
                                      denoise=options.denoise,
                                      sub_file=sub_file)
        else:
            if options.season_num:
                tv_season = options.season_num
            else:
                tv_season = input_parser.get_season(file)

            if options.episode_num:
                tv_episode = options.episode_num
            else:
                tv_episode = input_parser.get_episode(file)

            if options.out_file:
                options.out_file = Path(orig_out_file).with_suffix(f'.s{tv_season}e{tv_episode}.webm')

            if not input_parser.is_batch_repeat(prev_file, file):
                title = thetvdb_lookup.get_title(title)

            file_title, file_summary = thetvdb_lookup.get_file_metadata(title,
                                                                        tv_season,
                                                                        tv_episode)

            if int(stream_helpers.get_audio_ch(in_file=file, audio_id='0')) > 2:
                if options.burn_subs or not sub_file:
                    wrapper.TVMultiChannelWrapper(in_file=file,
                                                  out_file=options.out_file,
                                                  file_title=file_title,
                                                  file_summary=file_summary,
                                                  burn_subs=options.burn_subs,
                                                  crf=options.crf,
                                                  crop=options.crop,
                                                  denoise=options.denoise,
                                                  sub_file=sub_file)
                else:
                    wrapper.TVMultiChannelSubtitleWrapper(in_file=file,
                                                          out_file=options.out_file,
                                                          file_title=file_title,
                                                          file_summary=file_summary,
                                                          crf=options.crf,
                                                          crop=options.crop,
                                                          denoise=options.denoise,
                                                          sub_file=sub_file)
            else:
                if options.burn_subs or not sub_file:
                    wrapper.TVStereoWrapper(in_file=file,
                                            out_file=options.out_file,
                                            file_title=file_title,
                                            file_summary=file_summary,
                                            burn_subs=options.burn_subs,
                                            crf=options.crf,
                                            crop=options.crop,
                                            denoise=options.denoise,
                                            sub_file=sub_file)
                else:
                    wrapper.TVStereoSubtitleWrapper(in_file=file,
                                                    out_file=options.out_file,
                                                    file_title=file_title,
                                                    file_summary=file_summary,
                                                    crf=options.crf,
                                                    crop=options.crop,
                                                    denoise=options.denoise,
                                                    sub_file=sub_file)

        if options.del_orig:
            if options.ext_subs:
                print(f'Deleting external subtitle file: {sub_file}')
                sub_file.unlink()
            print(f'Deleting input file: {sub_file}')
            file.unlink()

        prev_file = file


if __name__ == '__main__':
    main()
