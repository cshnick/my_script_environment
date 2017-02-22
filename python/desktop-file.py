#!/usr/bin/python3

import logging as log
import os
from argparse import ArgumentParser
from fnmatch import fnmatch
from color.colorize import Color
import re
import imghdr

log.basicConfig(level=log.DEBUG if 'DEBUG' in os.environ else log.WARNING,
                format='%(asctime)s - %(levelname)s - %(message)s')


class DesktopFileResolver:
    HOME = os.path.expanduser('~')
    HABITAT = [
        HOME + '/.local/share/applications',
        HOME + '/.local/share/RecentDocuments/',
        HOME + '/.kde4/share/apps',
        HOME + '/.gnome/apps',
        '/usr/share/applications'
    ]
    STEAM_APPS = HOME + '/.steam/steam/steamapps/common'
    DEFAULT_EDITOR = '/usr/bin/kwrite'

    def __init__(self):
        self._args = None
        self._extend_habitat()

    @staticmethod
    def _extend_habitat():
        from os.path import join, isdir, exists
        from os import listdir

        def extend_sub(path):
            sublist = [join(path, fname) for fname in listdir(path) if isdir(join(path, fname))]
            if len(sublist):
                DesktopFileResolver.HABITAT.extend(sublist)

        [extend_sub(file) for file in DesktopFileResolver.HABITAT if exists(file)]

    def _operate(self, callback):
        callback.prev_dir = ''
        for hpath in self.HABITAT:
            for filename in os.listdir(hpath):
                if fnmatch(filename, '*.desktop'):
                    # Pass method attributes, not as parameters as they have to be mutable
                    setattr(callback, 'next_dir', hpath)
                    setattr(callback, 'prev_dir', callback.prev_dir)
                    setattr(callback, 'filename', filename)
                    callback()

    def search(self):
        pattern = self._args.search_args[0]
        regex = re.compile('(' + pattern + ')', re.IGNORECASE)

        def iter_cb(**kwargs):
            if regex.search(iter_cb.filename):
                if iter_cb.next_dir != iter_cb.prev_dir:
                    print('%s: ' % Color(iter_cb.next_dir).as_green())
                    iter_cb.prev_dir = iter_cb.next_dir
                print('\t%s' % regex.sub(Color('\\1').as_red(), iter_cb.filename))

        self._operate(iter_cb)

    def open(self):
        from subprocess import Popen

        pattern = self._args.search_args[0]
        regex = re.compile('(' + pattern + ')', re.IGNORECASE)
        editor = self.DEFAULT_EDITOR
        if 'EDITOR' in os.environ:
            editor = os.environ['EDITOR']

        def iter_cb(**kwargs):
            if regex.search(iter_cb.filename):
                fullpath = os.path.join(iter_cb.next_dir, iter_cb.filename)
                Popen([editor, fullpath])

        self._operate(iter_cb)

    def icons(self):
        from os.path import join, isdir, exists
        from os import listdir

        pattern = self._args.search_arg
        verbose = self._args.verbose
        regex = re.compile('(' + pattern + ')', re.IGNORECASE)
        games_match = [join(self.STEAM_APPS, fname) for fname in listdir(self.STEAM_APPS) if regex.search(fname)]
        for game in games_match:
            print('%s:' % Color(game).as_green())
            for p, d, files in os.walk(game):
                [print('\t%s' % join(p, regex.sub(Color('\\1').as_red(), fname)))
                 for fname in files
                 if imghdr.what(join(p, fname)) and (regex.search(fname) or verbose)]

    def main(self):
        parser = ArgumentParser("Search and open desktop files by patterns")

        subparsers = parser.add_subparsers(dest='callback')

        parser_search = subparsers.add_parser('search', help="search")
        parser_search.add_argument('search_args', help='Enter a rule for dbus subparser', nargs="+")

        parser_open = subparsers.add_parser('open', help='open')
        parser_open.add_argument('search_args', help='Enter search args for files to open', nargs='+')

        parser_icon = subparsers.add_parser('icons', help='print proposed icons')
        parser_icon.add_argument('search_arg', help='Enter search args for files to open')
        parser_icon.add_argument('-v', '--verbose', help="Print all not only pattern matched", action='store_true')

        self._args = parser.parse_args()

        callback = getattr(self, self._args.callback)
        if callback:
            callback()


if __name__ == '__main__':
    DesktopFileResolver().main()
