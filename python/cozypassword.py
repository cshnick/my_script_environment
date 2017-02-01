#!/usr/bin/python3

from sys import version_info
#python 2.x
if version_info.major < 3:
    import clipboard as clip
#pyrhon 3.x
else:
    import pyperclip as clip

from argparse import ArgumentParser
from cozy_password.resolver import ScandResolver
from os.path import basename
import logging as log
import json

class Const (object):
    Subprsr_name = 'subparser_name'
    Remote_update = 'remote_update'
    class Restore:
        Name = 'restore'
    class Add:
        Name = "add"
        Key = "Add.Key"
        Password  = "Add.Password"
    class Get:
        Name = "get"
        Key = "Get.Key"
    class Print:
        Name = "print"

class CmdCozyPassword (object):
    def __init__(self):
        filename = basename(__file__)
        parser = ArgumentParser(filename)
        parser.add_argument('-r', '--update_remote', help='update from remote repository', dest=Const.Remote_update, action='store_true')

        subparsers = parser.add_subparsers(help="Subparsers", dest=Const.Subprsr_name)
        parser_get = subparsers.add_parser(Const.Get.Name, help="Get password from key")
        parser_get.add_argument(Const.Get.Key, help='Get arguments')

        parser_add = subparsers.add_parser(Const.Add.Name, help="Add new key-password pair")
        parser_add.add_argument('-k', '--key', help='key(human readable)', dest=Const.Add.Key, required=True)
        parser_add.add_argument('-p', '--password', help='Password to store (generate if empty)', dest=Const.Add.Password)

        parser_restore = subparsers.add_parser(Const.Restore.Name, help="Attempt to restore(debug only)")

        parser_print = subparsers.add_parser(Const.Print.Name, help="Print as json")

        self._args =  parser.parse_args()
        self._resolver = ScandResolver()

        self._resolver.password = 'Qwerty#0'

        remote = getattr(self._args, Const.Remote_update, False)
        self._resolver.update(remote=remote)

    def __process_args(self):
        log.debug("Self args: %s" % self._args)
        #Callback is starting from process_...
        name  = 'process_'+self._args.__dict__[Const.Subprsr_name]
        callback = getattr(self, name)
        if callback:
            callback()

    def process_get(self):
        key = getattr(self._args, Const.Get.Key, None)
        password = self._resolver.password_for_name(key, '')
        clip.copy(password)

    def process_add(self):
        key = getattr(self._args, Const.Add.Key, None)
        password = getattr(self._args, Const.Add.Password, None)

        self._resolver.add_password(key=key, password=password)
        pass

    def process_restore(self):
        log.debug("Attempting to restore")
        self._resolver.restore()
        log.debug("Restored, no errors detected")

    def process_print(self):
        data = self._resolver.data()
        print(json.dumps(data['Pairs'], indent=1))


    def main(self):
        self.__process_args()
        log.debug("Clipboard content: %s" % clip.paste())

if __name__ == "__main__":
    cmd = CmdCozyPassword()
    cmd.main()
