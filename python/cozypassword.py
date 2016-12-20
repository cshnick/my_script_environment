#!/usr/bin/python

import clipboard
from argparse import ArgumentParser
from cozy_password.resolver import ScandResolver
from os import environ

class CmdCozyPassword (object):
    def __init__(self, get_args=None):
        parser = ArgumentParser("Cmd parser")
        subparsers = parser.add_subparsers(help="Subparser to fulfill functionality")
        parser_get = subparsers.add_parser('get', help="Get functionality")
        parser_get.add_argument('getargs', help='Get arguments', nargs="+")

        args = parser.parse_args()

        self.__get_args = args.getargs

        if len(self.__get_args):
            self.__process_get()


    def __process_get(self):
        key = self.__get_args[0]
        clipboard.copy(ScandResolver().password_for_name(key))


    def main(self):
        if "DEBUG" in environ:
            print("Clipboard content: %s" % clipboard.paste())


if __name__ == "__main__":
    cmd = CmdCozyPassword()
    cmd.main()
