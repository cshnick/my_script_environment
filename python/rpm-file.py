#!/usr/bin/python

__author__ = 'ilia'
from color.colorize import Color
import rpm
import argparse

def main():
    parser = argparse.ArgumentParser("rpm like behavior")

    subparsers = parser.add_subparsers(help="file-like option")

    parser_search = subparsers.add_parser('search', help="search")
    parser_search.add_argument('pattern', help='enter file pattern to find', nargs=1)

    args = parser.parse_args()

    pattern = args.pattern[0]

    ts = rpm.TransactionSet()
    mi = ts.dbMatch()
    for h in mi:
        package_name = h[rpm.RPMTAG_NAME]
        files = h[rpm.RPMTAG_FILENAMES]
        matches = []
        for fln in files:
            if pattern in fln:
                matches.append(fln.replace(pattern, Color(pattern).as_red()))


        if matches:
            print ('%s:' % Color(package_name).as_green())
            for match in matches:
                print ('\t%s' % match)


if __name__ == "__main__":
    main()