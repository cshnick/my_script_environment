#!/usr/bin/env python

import simplejson as json
import os

class ResolverBase(object):
    pass

class ScandResolver(ResolverBase):
    __Pairs = "Pairs"
    __Filename = "scand_map.json"
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


