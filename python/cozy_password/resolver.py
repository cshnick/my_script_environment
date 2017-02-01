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
from git import Repo
from git.repo.fun import is_git_dir
import git


log.basicConfig(level=log.DEBUG if 'DEBUG' in os.environ else log.WARNING,
                format='%(asctime)s - %(levelname)s - %(message)s')


class ResolverBase(object):
    pass

@contextmanager
def customopen(*args, **kwargs):
    """ Open file or buffer

    """
    io = kwargs['io']
    stream = open(*args) if io is 'file' else BytesIO()
    try:
        yield stream
    finally:
        stream.close()

def load_on_demand(method):
    def deco(self, *args, **kwargs):
        if not self.pairs:
            self.load()
        return method(self, *args, **kwargs)
    return deco

def init_repo(method):
    def deco(self, *args, **kwargs):
        self._pull()
        method(self, *args, **kwargs)
    return deco

def push_if_index(method):
    def deco(self, *args, **kwargs):
        method(self, *args, **kwargs)
        self._push()
    return deco


class ScandResolver(ResolverBase):
    _Filename = "scand_map.json"
    _Encrypted = "map.json.enc"
    _Dir_path = os.path.dirname(os.path.realpath(__file__))
    _Repo_path = _Dir_path + '/encoded'
    _Repo_remote_path = 'git@github.com:cshnick/encodedp.git'
    _Filename_path = _Dir_path + '/' + _Filename
    _Encrypted_path = _Repo_path + '/' + _Encrypted

    Pairs_tag = "Pairs"

    RepoPath = _Repo_path
    RepoRemote = _Repo_remote_path

    def __init__(self):
        """ Create resolver with empty data.
            Loading process is controled by user

        """
        super().__init__()
        self._filename = self._Filename
        self._encrypted_filename = self._Encrypted
        self._encrypted_dir = self._Repo_path
        self._enc_password = ''
        self._remote = self._Repo_remote_path
        self._data = {self.Pairs_tag : {}}

    @property
    def path(self):
        return os.path.join(self._encrypted_dir, self._encrypted_filename)
    @path.setter
    def path(self, value):
        self._encrypted_dir = os.path.dirname(value)
        self._encrypted_filename = os.path.basename(value)

    @property
    def password(self): return self._enc_password
    @password.setter
    def password(self, value): self._enc_password = value

    @property
    def remote(self):
        return self._remote
    @remote.setter
    def remote(self, value):
        self._remote = value

    @property
    def pairs(self):
        return self._data[self.Pairs_tag]


    def password_for_name(self, name, default=None):
        log.debug("password for name %s from %s" % (name, self.path))
        pairs = self._data[self.Pairs_tag]
        password = default
        if name in pairs:
            password = pairs[name]

        return password

    def add_password(self, key, password):
        log.debug("Inserting password")
        if password is None:
            password = generate_pass()

        self._data[ScandResolver.Pairs_tag][key] = password
        self.save()

    def save(self):
        self._save(io='buffer')

    def save_file(self):
        self._save(ScandResolver._Filename_path, 'r', io='file')

    def load(self):
        self._load(self._data, io='buffer')
        pass

    def load_from_file(self):
        self._load(ScandResolver._Filename_path, 'r+', io='file')
        pass

    def restore(self):
        with open(ScandResolver._Filename_path, 'rb') as scand_encrypted:
            with open(ScandResolver._Encrypted_path, 'wb') as scand_map_file:
                file_cryptor.encrypt(in_file=scand_encrypted,
                                     out_file=scand_map_file,
                                     password=b'Qwerty#0')

    def update(self, **kwargs):
        if 'remote' in kwargs and kwargs['remote'] is True:
            self._pull()
        self.load()

    def _save(self, *args, **kwargs):
        with customopen(*args, **kwargs) as source_io:
            with open(self.path, "wb") as enc_dest_io:
                value = source_io.getvalue()
                #fill buffer with json data
                if kwargs['source_io'] is 'buffer':
                    json_bytes = json.dumps(self._data).encode('utf-8')
                    source_io.write(json_bytes)
                    source_io.seek(0)

                file_cryptor.encrypt(in_file=source_io,
                                     out_file=enc_dest_io,
                                     password=self.password.encode('utf-8'))

    def _load(self, *args, **kwargs):
        with open(self.path, "rb") as enc_source_io:
            with customopen(*args, **kwargs) as destination_io:
                file_cryptor.decrypt(in_file=enc_source_io,
                                     out_file=destination_io,
                                     password=self.password.encode('utf-8'))

                destination_io.seek(0)
                decoded = destination_io.read().decode('utf-8')

                if decoded:
                    self._data = json.loads(decoded)

    def _pull(self):
        if not os.path.exists(ScandResolver.RepoPath + "/.git"):
            repo = Repo.clone_from(self._remote, self._encrypted_dir)
        else:
            class MyProgressPrinter(git.RemoteProgress):
                def update(self, op_code, cur_count, max_count=None, message=''):
                    log.debug("%s percents" % (cur_count / (max_count or 100.0) * 100))

            repo = Repo(self._encrypted_dir)
            origin = repo.remotes.origin
            for info in origin.pull(progress=MyProgressPrinter()):
                log.debug("Pulled %s to %s" % (info.ref, info.commit.message))

    def _push(self):
        repo = Repo(ScandResolver.RepoPath)
        index = repo.index
        entries = [path for path, stage in index.entries if not stage]
        index.add(entries)
        if entries:
            import datetime
            import socket
            index.commit('%s - from %s' % (datetime.datetime.now(), socket.gethostname()))
            origin = repo.remotes.origin
            for info in origin.push():
                log.debug("Pushed %s" % info.commit.message)