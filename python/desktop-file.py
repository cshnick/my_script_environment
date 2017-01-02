#!/usr/bin/python3

import logging as log
import os
from argparse import ArgumentParser
from fnmatch import fnmatch
from color.colorize import Color
import re

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
    DEFAULT_EDITOR='/usr/bin/kwrite'

    def __init__(self):
        self.__args = None
        self.__extend_habitat()

    @staticmethod
    def __extend_habitat():
        from os.path import join, isdir
        from os import listdir

        def extend_sub(path):
            sublist = [join(path, fname) for fname in listdir(path) if isdir(join(path, fname))]
            if len(sublist):
                DesktopFileResolver.HABITAT.extend(sublist)

        for file in DesktopFileResolver.HABITAT:
            if os.path.exists(file):
                extend_sub(file)

    def __operate(self, callback):
        callback.prev_dir=''
        for hpath in self.HABITAT:
            for filename in os.listdir(hpath):
                if fnmatch(filename, '*.desktop'):
                    setattr(callback, 'next_dir', hpath)
                    setattr(callback, 'prev_dir', callback.prev_dir)
                    setattr(callback, 'filename', filename)
                    bef = callback.prev_dir
                    log.debug("Bef: %s" % bef)
                    callback()
                    af = callback.prev_dir
                    log.debug("Af: %s\n" % af)


    def search(self):
        pattern = self.__args.search_args[0]
        regex = re.compile('(' + pattern + ')', re.IGNORECASE)

        def iter_cb(**kwargs):
            if regex.search(iter_cb.filename):
                if iter_cb.next_dir != iter_cb.prev_dir:
                    print('%s: ' % Color(iter_cb.next_dir).as_green())
                    iter_cb.prev_dir = iter_cb.next_dir
                print('\t%s' % regex.sub(Color('\\1').as_red(), iter_cb.filename))

        self.__operate(iter_cb)

    def open(self):
        from subprocess import Popen

        pattern = self.__args.search_args[0]
        regex = re.compile('(' + pattern + ')', re.IGNORECASE)
        editor = self.DEFAULT_EDITOR
        if 'EDITOR' in os.environ:
            editor = os.environ['EDITOR']

        def iter_cb(**kwargs):
            if regex.search(iter_cb.filename):
                fullpath = os.path.join(iter_cb.next_dir, iter_cb.filename)
                Popen([editor, fullpath])

        self.__operate(iter_cb)


    def main(self):
        parser = ArgumentParser("Search and open desktop files by patterns")

        subparsers = parser.add_subparsers(dest='callback')

        parser_search = subparsers.add_parser('search', help="search")
        parser_search.add_argument('search_args', help='Enter a rule for dbus subparser', nargs="+")

        parser_open = subparsers.add_parser('open', help='open')
        parser_open.add_argument('search_args', help='Enter search args for files to open', nargs='+')

        self.__args = parser.parse_args()

        callback = getattr(self, self.__args.callback)
        if callback:
            callback()


if __name__ == '__main__':
    DesktopFileResolver().main()
