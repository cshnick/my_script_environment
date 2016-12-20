#!/usr/bin/env python

import simplejson as json
import os
import file_cryptor
import cStringIO

class ResolverBase(object):
    pass

class ScandResolver(ResolverBase):
    __Pairs = "Pairs"
    __Filename = "scand_map.json"
    __Encrypted = "scand_map.json.enc"
    __Dir_path = os.path.dirname(os.path.realpath(__file__))

    def password_for_name(self, name):
        if "DEBUG" in os.environ:
            print ("Dir path: %s" % ScandResolver.__Dir_path)
        with open(ScandResolver.__Dir_path + "/" + ScandResolver.__Filename) as scand_map_file:
            scand_map = json.load(scand_map_file)

        password = None
        if name in scand_map[ScandResolver.__Pairs]:
            password = scand_map[ScandResolver.__Pairs][name]

        return password

    def save(self):
        with open(ScandResolver.__Dir_path + "/" + ScandResolver.__Filename) as scand_map_file:
            with open(ScandResolver.__Dir_path + "/" + ScandResolver.__Encrypted, "w") as scand_encrypted:
                file_cryptor.encrypt(in_file=scand_map_file,
                                     out_file=scand_encrypted,
                                     password="Qwerty#0")

    def restore(self):
        with open(ScandResolver.__Dir_path + "/" + ScandResolver.__Encrypted, "r") as scand_encrypted:
            with open(ScandResolver.__Dir_path + "/" + ScandResolver.__Filename, "w") as scand_map_file:
                file_cryptor.decrypt(in_file=scand_encrypted,
                                     out_file=scand_map_file,
                                     password="Qwerty#0")

