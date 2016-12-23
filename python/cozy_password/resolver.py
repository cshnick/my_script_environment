#!/usr/bin/env python

import simplejson as json
import os
import file_cryptor
from cStringIO import StringIO
from contextlib import contextmanager
from password_generator import generate_pass
from decorator import decorator

class ResolverBase(object):
    pass

#Open 'file' or 'buffer'
@contextmanager
def customopen(*args, **kwargs):
    stream = open(*args) if type is 'file' else StringIO()
    try:
        yield stream
    finally:
        stream.close()

@decorator
def dec1(fn, *args, **kwargs):
    if len(args) is 1:
        return fn(args[0], **kwargs)
    return fn(*args, **kwargs)


def load_on_demand(method):
    def deco(self, *args, **kwargs):
        if not hasattr(self, "__data") or not self.__data:
            self.load()
        return method(self, *args, **kwargs)
    return deco


class ScandResolver(ResolverBase):
    __Pairs = "Pairs"
    __Filename = "scand_map.json"
    __Encrypted = "scand_map.json.enc"
    __Dir_path = os.path.dirname(os.path.realpath(__file__))
    __Filename_path = __Dir_path + '/' + __Filename
    __Encrypted_path = __Dir_path + '/' + __Encrypted

    def __init__(self):
        #self.restore()
        self.__data = None

    @load_on_demand
    def password_for_name(self, name, secondarg=None):
        if "DEBUG" in os.environ:
            print ("Dir path: %s" % ScandResolver.__Dir_path)
        pairs = self.__data[ScandResolver.__Pairs]
        password = None
        if name in pairs:
            password = pairs[name]

        return password

    @load_on_demand
    def add_password(self, key, password):
        if "DEBUG" in os.environ:
            print ("Inserting password")

        if password is None:
            password = generate_pass()

        self.__data[ScandResolver.__Pairs][key] = password
        self.save()

    def __save(self, *args, **kwargs):
        with customopen(*args, **kwargs) as scand_map_file:
            with open(ScandResolver.__Encrypted_path, "w") as scand_encrypted:
                value = scand_map_file.getvalue()
                if kwargs['type'] is 'buffer':
                    json.dump(self.__data, scand_map_file)
                    scand_map_file.seek(0)

                file_cryptor.encrypt(in_file=scand_map_file,
                                     out_file=scand_encrypted,
                                     password="Qwerty#0")

    def __load(self, *args, **kwargs):
        with open(ScandResolver.__Encrypted_path, "r") as scand_encrypted:
            with customopen(*args, **kwargs) as scand_map_file:
                file_cryptor.decrypt(in_file=scand_encrypted,
                                     out_file=scand_map_file,
                                     password="Qwerty#0")

                scand_map_file.seek(0)
                self.__data = json.load(scand_map_file)


    def save(self):
        self.__save(type='buffer')

    def save_file(self):
        self.__save(ScandResolver.__Filename_path, 'r', type='file')

    def load(self):
        self.__load(self.__data, type='buffer')
        pass

    def load_from_file(self):
        self.__load(ScandResolver.__Filename_path, 'r+', type='file')
        pass

    def restore(self):
        with open(ScandResolver.__Filename_path, "r") as scand_encrypted:
            with open(ScandResolver.__Encrypted_path, "w") as scand_map_file:
                file_cryptor.encrypt(in_file=scand_encrypted,
                                     out_file=scand_map_file,
                                     password="Qwerty#0")







