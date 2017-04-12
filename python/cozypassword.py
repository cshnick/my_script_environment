#!/usr/bin/python3
#PYTHON_ARGCOMPLETE_OK

from sys import version_info

from sys import exit
from argparse import ArgumentParser
from cozy_password.resolver import ScandResolver
from os.path import basename
import logging as log
import json
from getpass import getpass
import argcomplete

# python 2.x
if version_info.major < 3:
    import clipboard as clip
# pyrhon 3.x
else:
    import pyperclip as clip


class Const(object):
    Subprsr_name = 'subparser_name'
    Remote_update = 'remote_update'
    Password = "ext_passwd"

    class Restore:
        Name = 'restore'

    class Add:
        Name = "add"
        Key = "Add.Key"
        Password = "Add.Password"

    class Set:
        Name = 'set'
        Key = 'Set.Key'
        Password = 'Set.Password'

    class Del:
        Name = 'del'
        Key = 'Del.Key'

    class Rename:
        Name = 'rename'
        OldName = 'Ren.OldName'
        NewName = 'Ren.NewName'

    class Get:
        Name = "get"
        Key = "Get.Key"

    class Print:
        Name = "print"

    class CheckPasword:
        Name = 'check_password'
        Key = 'Check.Key'

    class Load:
        Name = 'load'
        File = 'Load.File'


class PasswordError(Exception):
    def __init__(self, message):
        super().__init__(message)


class CmdCozyPassword(object):
    def __init__(self):
        filename = basename(__file__)
        parser = ArgumentParser(filename)
        parser.add_argument('-r', '--update_remote', help='update from remote repository', dest=Const.Remote_update,
                            action='store_true')

        subparsers = parser.add_subparsers(help="Subparsers", dest=Const.Subprsr_name)
        parser_get = subparsers.add_parser(Const.Get.Name, help="Get password from key")
        parser_get.add_argument(Const.Get.Key, help='Get arguments')

        parser_add = subparsers.add_parser(Const.Add.Name, help="Add new key-password pair")
        parser_add.add_argument('-k', '--key', help='key(human readable)', dest=Const.Add.Key, required=True)
        parser_add.add_argument('-p', '--password', help='Password to store (generate if empty)',
                                dest=Const.Add.Password)

        parser_set = subparsers.add_parser(Const.Set.Name, help="Set key-password pair")
        parser_set.add_argument('-k', '--key', help='key(human readable)', dest=Const.Set.Key, required=True)
        parser_set.add_argument('-p', '--password', help='Password to store (generate if empty)',
                                dest=Const.Set.Password)

        parser_del = subparsers.add_parser(Const.Del.Name, help="Delete key-password pair")
        parser_del.add_argument(Const.Del.Key, help='key(human readable)')

        parser_ren = subparsers.add_parser(Const.Rename.Name, help="Rename specified key")
        parser_ren.add_argument(Const.Rename.OldName, help='old name')
        parser_ren.add_argument(Const.Rename.NewName, help='new name')

        parser_restore = subparsers.add_parser(Const.Restore.Name, help="Attempt to restore(debug only)")

        parser_print = subparsers.add_parser(Const.Print.Name, help="Print as json")

        parser_chck_password = subparsers.add_parser(Const.CheckPasword.Name, help="Check password")
        parser_chck_password.add_argument(Const.CheckPasword.Key, help='Password to check')

        parser_load = subparsers.add_parser(Const.Load.Name, help="load from uncompressed file")
        parser_load.add_argument(Const.Load.File, help='Password to check')


        self._args = parser.parse_args()
        self._resolver = ScandResolver()
        self._resolver.read_config()
        self._resolver.remote_update = getattr(self._args, Const.Remote_update, False)
        self._resolver.password = getpass()
        self._resolver.update()
        if not self._resolver.check_password(self._resolver.password):
            raise PasswordError("Incorrect password")

    def _process_args(self):
        log.debug("Self args: %s" % self._args)
        # Callback is starting from process_...
        name = 'process_' + self._args.__dict__[Const.Subprsr_name]
        callback = getattr(self, name)
        if callback:
            callback()

    def process_get(self):
        key = getattr(self._args, Const.Get.Key, None)
        password = self._resolver.password_for_name(key, '')
        if (password):
            clip.copy(password)
            log.debug("Clipboard content: %s" % clip.paste())

    def process_add(self):
        key = getattr(self._args, Const.Add.Key, None)
        password = getattr(self._args, Const.Add.Password, None)
        self._resolver.add_password(key=key, password=password)
        pass

    def process_set(self):
        key = getattr(self._args, Const.Set.Key, None)
        password = getattr(self._args, Const.Set.Password, None)
        self._resolver.set_password(key=key, password=password)
        pass

    def process_del(self):
        key = getattr(self._args, Const.Del.Key, None)
        self._resolver.del_item(key=key)
        pass

    def process_rename(self):
        old = getattr(self._args, Const.Rename.OldName, None)
        new = getattr(self._args, Const.Rename.NewName, None)
        self._resolver.rename_key(old, new)

    def process_restore(self):
        log.debug("Attempting to restore")
        log.debug("Restored, no errors detected, or detected?")

    def process_print(self):
        pairs = self._resolver.pairs
        print(json.dumps(pairs, indent=1))

    def process_check_password(self):
        key = getattr(self._args, Const.CheckPasword.Key, None)
        result = bool(self._resolver.check_password(key))
        print('Password ok' if result else 'Password does not match, try again')

    def process_load(self):
        filename = getattr(self._args, Const.Load.File, None)
        result = self._resolver.from_file(filename)

    def main(self):
        self._process_args()


if __name__ == "__main__":
    try:
        cmd = CmdCozyPassword()
        cmd.main()
    except PasswordError as passerr:
        print(passerr)
    except RuntimeError as runtimeerr:
        print(runtimeerr)
    except KeyboardInterrupt:
        exit(0)
