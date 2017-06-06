#!/usr/bin/python

from color.colorize import colorize
from color.colorize import term_color as col
import argparse
from color.colorize import Color
from collections import defaultdict
import sys
import os.path

__author__ = 'ilia'


class IAction(argparse.Action):
    def __print_value_for_option(self, option, value):
        frmt = 'VALUE %s'
        if option == '-I':
            frmt = Color('INCLUDEPATH += %s').as_green()
        elif option == '-include':
            frmt = Color('INCLUDES += %s').as_yellow()
        elif option == '-D':
            frmt = Color('DEFINES += %s').as_cyan()
        elif option == '-f':
            frmt = Color('f FLAGS += %s').as_purple()
        elif option == '-M':
            frmt = Color('M FlAGS += %s').as_blue()
        elif option == '-o':
            frmt = Color('Program name: %s').as_red()
        elif option == '-W':
            frmt = Color('W flags += %s').as_white()
        elif option == '-O':
            frmt = Color('Optimization: %s').as_yellow()
        elif option == '-std':
            frmt = Color('-std=%s').as_white()
        elif option in '-pipe -pthread -c -g'.split():
            frmt = Color(option).as_white()
        print(frmt % value)

    def __call__(self, parser, namespace, values, option_string=None):
        self.__print_value_for_option(option_string, values)
        if not hasattr(namespace, self.dest):
            setattr(namespace, self.dest, values)
        else:
            attr = getattr(namespace, self.dest)
            if attr == None:
                attr = []
            attr.append(values)
            setattr(namespace, self.dest, attr)


class CommonParser(object):
    def __init__(self):
        self._parser = argparse.ArgumentParser(description='Cmd arguments parser')
        self._parser.add_argument('-I', action=IAction, dest="Includepath")
        self._parser.add_argument("-include", action=(IAction), dest="INCLUDES")
        self._parser.add_argument("-D", action=IAction, dest="Definitions")
        self._parser.add_argument("-f", action=IAction, dest="Fs", help="Additional linker flags")
        self._parser.add_argument("-M", action=IAction, dest="MFlags", help="M flags")
        self._parser.add_argument("-o", action=IAction, dest="prog_nme", help="Specify the program name")
        self._parser.add_argument("-std", action=IAction, dest="std_spec", help="std compat mode")
        self._parser.add_argument("-W", action=IAction, dest="w_flags", help="W flags")
        self._parser.add_argument('-O', dest='optimization_val', help='optimization option', action=IAction)
        self._parser.add_argument('-pipe', dest='pipe_val', help='pipe option', action=IAction, const=True, nargs=0,
                                  required=False)
        self._parser.add_argument('-pthread', dest='pthread_val', help='pthread option', action=IAction, const=True,
                                  nargs=0, required=False)
        self._parser.add_argument('-g', dest='debug_val', help='debug', action=IAction, const=True, nargs=0,
                                  required=False)
        self._args = None

    def parse_args(self, str_args):
        self._args = self._parser.parse_args(str_args.split())
        return self._args

    def args(self):
        return self._args


class CompileParser(CommonParser):
    def __init__(self):
        super(CompileParser, self).__init__()
        self._parser.add_argument('file_name', help='filename to parse', nargs=1)
        self._parser.add_argument('-c', dest='compile_val', help='compile only', action=IAction, const=True, nargs=0,
                                  required=False)


class LinkParser(CommonParser):
    def __init__(self):
        super(LinkParser, self).__init__()
        self._parser.add_argument('-r', dest='r_flags', help='-r flags', action=IAction)
        self._parser.add_argument('-L', dest='ldir_flags', help='Linker directory flags', action=IAction)
        self._parser.add_argument('-l', dest='lfile_flags', help='Linker library flags', action=IAction)


def mergeDicts(dict1, dict2):
    res = defaultdict(list)
    for k, v in dict1.items():
        if not res[k].contains(v):
            res[k].append(v)
    for k, v in dict2.items():
        if not res[k].contains(v):
            res[k].append(v)

    return res


def merge_args(arg1, arg2):
    if not arg1 and arg2:
        return arg2
    if not arg2 and arg1:
        return arg1

    res = arg1
    return res


def parse_target(target_name, file_obj):
    parse_next = False
    invoke_method = None
    t_args = None
    for ln in file_obj.readlines():
        if ln.endswith('\n'):
            ln = ln[:-1]
        if parse_next:
            # cludge
            if ln.startswith('make'):
                continue
            if invoke_method:
                targs = merge_args(t_args, invoke_method(target_name, ln))
                invoke_method = None
            parse_next = False

        if ln.startswith(target_name):
            parse_next = True
            if ln == target_name:
                invoke_method = parse_link
            else:
                invoke_method = parse_compile


def parse_compile(target_name, fline):
    print('parse compile %s:%s' % (target_name, fline))
    # clean unused elements
    fline = fline.replace('c++ ', '', 1)
    fline = fline.replace('.deps/' + target_name + '.o.pp', '', 1)

    parser = CompileParser()
    t_args = parser.parse_args(fline)

    return t_args


def parse_link(target_name, fline):
    print('parse link %s:%s' % (target_name, fline))

    # clean unused elements
    fline = fline.split('-- ', 1)[1]
    to_replace = 'c++ ' + target_name + '.o'
    for v in to_replace.split():
        fline = fline.replace(v, '', 1)

    parser = LinkParser()
    t_args = parser.parse_args(fline)

    return t_args


def main():
    @colorize(col.blue)
    def start():
        return "Started\n-------"

    @colorize(col.blue)
    def finished():
        return "--------\nFinished"

    print(start())

    m_parser = argparse.ArgumentParser(description='Main parser')
    m_parser.add_argument('--file', help='Filename to retrieve string')
    m_parser.add_argument('--target', help='Target')

    m_args = m_parser.parse_args()

    in_file = sys.stdin
    if m_args.file:
        file_name = m_args.file
        if not os.path.exists(file_name):
            raise Exception("File %s does not exist" % sys.argv[1])
        in_file = open(m_args.file)

    print('file no %s' % in_file.fileno())

    if m_args.target:
        target = m_args.target
        parse_target(target_name=target, file_obj=in_file)
        return 0

    print(finished())


if __name__ == '__main__':
    main()
