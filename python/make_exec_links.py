#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os.path as osp
import subprocess as sbp
import os
import sys

thismod = sys.modules[__name__]


def entries(path: str, triple_index: int):
    lvl: int = path.count(osp.sep)
    for triple in os.walk(path):
        if triple[0].count(osp.sep) > lvl: break
        return triple[triple_index]
    return None


def dirs(path):
    return entries(path, triple_index=1)


def files(path):
    return entries(path, triple_index=2)


def is_exe(path):
    return os.path.isfile(path) and os.access(path, os.X_OK)


class LinkMakerException(Exception):
    pass


def default_execs(path):
    def form_exec_name(input):
        basename = osp.basename(input)
        fine_name = basename.lower()
        fine_name = fine_name.replace('_', '-')
        fine_name, _ = osp.splitext(fine_name)
        return fine_name

    fine_files = list(filter(lambda tpath: is_exe(path + '/' + tpath), files(path)))
    fine_names = list(map(lambda tpath: form_exec_name(tpath), fine_files))

    return zip(fine_files, fine_names)


def python_execs(path):
    return default_execs(path)


def get_dir_processor(name):
    class_name = name + '_execs'
    return getattr(thismod, class_name, default_execs)


class LinkMaker(object):
    DIRS_ALLOWED = ['bash', 'python']

    def __init__(self):
        self._args: argparse.Namespace = None

        self.source: str = None
        self.destination: str = None

    def main(self):
        self.parse_args()
        self.process_args()
        self.ln_s_execs()

    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--source", help="scripts directory", required=True)
        parser.add_argument("--destination", help="destination for links directory", required=True)
        self._args = parser.parse_args()

    def process_args(self):
        self.source = osp.abspath(osp.expanduser(self._args.source))
        self.destination = osp.abspath(osp.expanduser(self._args.destination))

    def ln_s_execs(self):
        all_dirs = dirs(self.source)
        filtered = list(filter(lambda name: name in LinkMaker.DIRS_ALLOWED, all_dirs))
        if len(filtered) < len(LinkMaker.DIRS_ALLOWED):
            raise LinkMakerException('Make sure each [%s] file exists in %s'
                                     % (','.join(LinkMaker.DIRS_ALLOWED), self.source))
        for name in filtered:
            full_name = self.source + '/' + name
            specific_execs = get_dir_processor(name)
            exec_tups = list(specific_execs(full_name))

            def ln_s(tup): sbp.call(['ln', '-s', full_name + '/' + tup[0], self.destination + '/' + tup[1]])

            [ln_s(tup) for tup in exec_tups]

    def __str__(self):
        return json.dumps(
            {
                'source': self.source,
                'destination': self.destination
            }
            , indent=4)

    def print(self):
        print(self)
        print(dir())


if __name__ == "__main__":
    LinkMaker().main()
