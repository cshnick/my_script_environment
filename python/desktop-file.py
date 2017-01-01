#!/usr/bin/python3

import logging as log
import os
from argparse import ArgumentParser

log.basicConfig(level=log.DEBUG if 'DEBUG' in os.environ else log.WARNING,
                format='%(asctime)s - %(levelname)s - %(message)s')


class DesktopFileResolver:
    HOME=os.path.expanduser('~')
    HABITAT= [
        HOME + '/.local/share/applications',
        HOME + '/.local/share/RecentDocuments/',
        HOME + '/.kde4/share/apps',
        HOME + '/.kde4/share/apps/RecentDocuments',
        HOME + '/.gnome/apps',
        '/usr/share/applications'
    ]


    def __init__(self):
        self.__args = None

    def expand_habitat(self):
        for file in DesktopFileResolver.HABITAT:
            if os.path.exists(file):
                #for sub in os.path.
                pass

    def main(self):
        parser = ArgumentParser("Search and open desktop files by patterns")

        subparsers = parser.add_subparsers()

        parser_search = subparsers.add_parser('dbus', help="search")
        parser_search.add_argument('rule_args', help='Enter a rule for dbus subparser', nargs="+")

        self.__args = parser.parse_args()

        pass


if __name__ == '__main__':
    DesktopFileResolver().main()