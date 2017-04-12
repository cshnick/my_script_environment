#!/usr/bin/python3

from argparse import ArgumentParser
import logging
import os
import json


class ArgBase(object):
    logging.basicConfig(level=logging.INFO if 'DEBUG' in os.environ else logging.WARNING,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    SUBPARSERS = 'subparsers'

    def __init__(self):
        self._args = None
        self._parse_args()

    def _parse_args(self):
        logging.debug('_parse_args base')
        pass


class YakuakeControl(ArgBase):
    """
    Yakyake control program via dbus
    """
    _FROM_CONF = 'from_conf'
    _FILENAME = 'filename'

    _SESSIONS_TAG = 'sessions'
    _WORKING_DIR_TAG = 'working_dir'

    def __init__(self):
        super().__init__()

        self._conf = None

    def _parse_args(self):
        parser = ArgumentParser("Yakuake dbus helper")
        subparsers = parser.add_subparsers(help='Control methods', dest=self.SUBPARSERS)

        from_conf = subparsers.add_parser(self._FROM_CONF, help='read from configuration file')
        from_conf.add_argument(self._FILENAME, help='Configuration filename')

        self._args = parser.parse_args()

    def main(self):
        pass


if __name__ == '__main__':
    YakuakeControl().main()
