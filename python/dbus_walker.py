#!/usr/bin/python3
# PYTHON_ARGCOMPLETE_OK

import argparse
import argcomplete
from argparse_ex import ArgparserBase, SUBPARSERS
import dbus
import dbus.bus
import os
import os.path as osp
import sys
import xmltodict
import collections

_PRINT_PARSER = 'print'
_SESSION_BUS_PARSER = 'session_bus'
_SYSTEM_BUS_PARSER = 'system_bus'
_ACTIVATABLE_NAMES = 'activatable_names'
_TEXT_ARGUMENT = 'text'

_NODE_TAG = 'node'
_INTERFACE_TAG = 'interface'
_NAME_TAG = '@name'

_INTROSPECTABLE = 'org.freedesktop.DBus.Introspectable'

_this_module = sys.modules[__name__]


def introspect(bus, obj, path):
    proxy = bus.get_object(obj, path)
    iface = dbus.Interface(proxy, dbus_interface=_INTROSPECTABLE)
    introspect_dict = xmltodict.parse(iface.Introspect())[_NODE_TAG]
    result = []
    for k in introspect_dict:
        def extend_names(item):
            process_name = lambda x: x if k == _INTERFACE_TAG else osp.join(path, x)
            if isinstance(item, list):
                result.extend([process_name(value[_NAME_TAG]) for value in item])
            elif isinstance(item, collections.OrderedDict):
                result.append(process_name(item[_NAME_TAG]))

        extend_names(introspect_dict[k])
    return result


class ChoicesCompleter(object):
    def __call__(self, parsed_args, parser, action, prefix, **kwargs):
        with open('trace.log', 'w') as flog:
            bus_string = parsed_args.__dict__[SUBPARSERS]
            flog.write('bus prefix: %s\n' % prefix)
            flog.write('bus string: %s\n' % bus_string)
            flog.write('bus action: %s\n' % action)
            flog.write('bus pargs1  : %s\n' % parsed_args)
            bus = dbus.SessionBus() if bus_string == _SESSION_BUS_PARSER else dbus.SystemBus()
            names = parsed_args.__dict__[_ACTIVATABLE_NAMES]
            if not names:
                return bus.list_names()
            elif len(names) == 1:
                intro_list = introspect(bus, names[0], '/')
                flog.write('introspect result %s' % intro_list)
                return intro_list


class Processor(ArgparserBase):
    def __init__(self):
        super().__init__()

        self._bus = None

    def _init_args(self):
        parser = argparse.ArgumentParser()

        introspect(dbus.SessionBus(), 'org.kde.krunner', '/KIO')
        subparsers = parser.add_subparsers(help='main processing commands', dest=SUBPARSERS)

        parser_add = subparsers.add_parser(_PRINT_PARSER)
        parser_add.add_argument(_TEXT_ARGUMENT, help='Test string')

        parser_session_bus = subparsers.add_parser(_SESSION_BUS_PARSER, help='session bus')
        parser_session_bus.add_argument(_ACTIVATABLE_NAMES, nargs='+').completer = ChoicesCompleter()

        parser_system_bus = subparsers.add_parser(_SYSTEM_BUS_PARSER, help='system bus')
        parser_system_bus.add_argument(_ACTIVATABLE_NAMES, nargs='+').completer = ChoicesCompleter()

        argcomplete.autocomplete(parser)
        self._args = parser.parse_args()

    def process_print(self):
        self.log('process_text')
        pass

    def process_session_bus(self):
        self.log('process_session_bus')
        self._bus = dbus.SessionBus()
        self._get_names()
        pass

    def process_system_bus(self):
        self.log('process_system_bus')
        self._bus = dbus.SystemBus()
        self._get_names()

    def _get_names(self):
        [self.log(name) for name in self._bus.list_activatable_names()]


if __name__ == "__main__":
    Processor().main()
