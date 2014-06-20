#!/usr/bin/python

__author__ = 'ilia'
from color.colorize import Color
import argparse
import os
import subprocess
import time

import gobject
gobject.threads_init()
from dbus import glib
glib.init_threads()
import dbus

class RulesDict:
    #Callable methods
    #Begin
    def newLeftTab(self):
        self.__newTab(0)
    def newRightTab(self):
        self.__newTab(1)
    #End callable methods

    ##### Helper functions #####
    #0 -left, 1-right
    def __newTab(self, side):
        side_string = 'left' if side == 0 else 'right'
        def run_pm():
            return self.bus.get_object(self.krusader_name, '/Instances/krusader/' + side_string + '_manager')
        panel_manager = self.__retrieve_with_try(run_pm)
        panel_manager.newTab(os.getcwd())
        krusdr = self.bus.get_object(self.krusader_name, '/Instances/krusader')
        krusdr.isRunning()


    def __retrieve_with_try(self, callback):
        try:
            result = callback()
        except: #krusader is not running
            subprocess.Popen(self.krusader_path.split(' '), close_fds=True, stderr=open(os.devnull,"w"))
            self.__wait_krusader()
            result = callback()

        return result

    def __wait_krusader(self):
        dbus_obj = self.bus.get_object('org.freedesktop.DBus', '/')
        for i in range(1, 100):
            if dbus_obj.NameHasOwner(self.krusader_name):
                return
            time.sleep(0.09)
        raise Exception('Ran out of time waiting for ' + self.krusader_name + 'to start.')

    def invoke_rule(self, name):
        #print 'invoking %s' % name
        self.func = getattr(RulesDict, name)
        if self.func:
            self.func(self)

    def __init__(self):
        self.bus = dbus.SessionBus()
        self.krusader_name = 'org.krusader'
        self.krusader_path = '/usr/bin/krusader'


def main():
    parser = argparse.ArgumentParser("DE interaction with krusader")

    subparsers = parser.add_subparsers(help="file-like option")

    parser_search = subparsers.add_parser('dbus', help="search")
    parser_search.add_argument('rule_name', help='Enter a rule for dbus subparser', nargs=1)

    args = parser.parse_args()
    rule_name = args.rule_name[0]

    rd = RulesDict()
    rd.invoke_rule(rule_name)


if __name__ == "__main__":
    main()