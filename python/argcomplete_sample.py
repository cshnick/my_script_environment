#!/usr/bin/python3
# PYTHON_ARGCOMPLETE_OK

import argparse
import argcomplete
from argparse_ex import ArgparserBase, SUBPARSERS
import logging as log

_PRINT_PARSER = 'print'
_TEXT_ARGUMENT = 'text'


class Processor(ArgparserBase):
    def __init__(self):
        super().__init__()

    def _init_args(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(help='main processing commands', dest=SUBPARSERS)

        parser_add = subparsers.add_parser(_PRINT_PARSER)
        parser_add.add_argument(_TEXT_ARGUMENT, help='Test string')

        argcomplete.autocomplete(parser)
        self._args = parser.parse_args()

    def process_print(self):
        log.debug('process_text')
        pass


if __name__ == "__main__":
    Processor().main()
