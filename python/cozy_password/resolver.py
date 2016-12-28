#!/usr/bin/env python

from sys import version_info
#python 2.x
if version_info.major < 3:
    from cStringIO import BytesIO
    pass
else:
#python 3.x
    from io import BytesIO
import os
import cozy_password.file_cryptor as file_cryptor
from contextlib import contextmanager
from cozy_password.password_generator import generate_pass
import logging as log
import json

log.basicConfig(level=log.DEBUG if 'DEBUG' in os.environ else log.WARNING,
                format='%(asctime)s - %(levelname)s - %(message)s')


class ResolverBase(object):
    pass

#Open 'file' or 'buffer'
@contextmanager
def customopen(*args, **kwargs):
    stream = open(*args) if type is 'file' else BytesIO()
    try:
        yield stream
    finally:
        stream.close()

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
    def password_for_name(self, name, default=None):
        log.debug("Dir path: %s" % ScandResolver.__Dir_path)
        pairs = self.__data[ScandResolver.__Pairs]
        password = default
        if name in pairs:
            password = pairs[name]

        return password

    @load_on_demand
    def add_password(self, key, password):
        log.debug("Inserting password")
        if password is None:
            password = generate_pass()

        self.__data[ScandResolver.__Pairs][key] = password
        self.save()

    def __save(self, *args, **kwargs):
        with customopen(*args, **kwargs) as scand_map_file:
            with open(ScandResolver.__Encrypted_path, "wb") as scand_encrypted:
                value = scand_map_file.getvalue()
                if kwargs['type'] is 'buffer':
                    json_bytes = json.dumps(self.__data).encode('utf-8')
                    scand_map_file.write(json_bytes)
                    scand_map_file.seek(0)

                file_cryptor.encrypt(in_file=scand_map_file,
                                     out_file=scand_encrypted,
                                     password=b'Qwerty#0')

    def __load(self, *args, **kwargs):
        with open(ScandResolver.__Encrypted_path, "rb") as scand_encrypted:
            with customopen(*args, **kwargs) as scand_map_file:
                file_cryptor.decrypt(in_file=scand_encrypted,
                                     out_file=scand_map_file,
                                     password=b'Qwerty#0')

                scand_map_file.seek(0)
                decoded = scand_map_file.read().decode('utf-8')
                self.__data = json.loads(decoded)


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
        with open(ScandResolver.__Filename_path, 'rb') as scand_encrypted:
            with open(ScandResolver.__Encrypted_path, 'wb') as scand_map_file:
                file_cryptor.encrypt(in_file=scand_encrypted,
                                     out_file=scand_map_file,
                                     password=b'Qwerty#0')

    @load_on_demand
    def data(self):
        return self.__data







