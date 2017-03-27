#!/usr/bin/env python

import os
import cozy_password.file_cryptor as file_cryptor
from contextlib import contextmanager
from cozy_password.password_generator import generate_pass
import logging as log
import json
from git import Repo
import git
import time
from io import BytesIO

log.basicConfig(level=log.INFO if 'DEBUG' in os.environ else log.WARNING,
                format='%(asctime)s - %(levelname)s - %(message)s')


class ResolverBase(object):
    pass


class DecodeError(Exception):
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


def profile(method):
    def deco(self, *args, **kwargs):
        start_time = time.time()
        ret = method(self, *args, **kwargs)
        elapsed_time = time.time() - start_time
        log.info('PROFILE - Method: %s, args: %s, elapsed: %s' % (method.__name__, args, elapsed_time))
        return ret

    return deco


def pull_if_required(method):
    def deco(self, *args, **kwargs):
        if self._remote_update:
            self._pull()
        return method(self, *args, **kwargs)

    return deco


def push_if_required(method):
    def deco(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        if self._remote_update:
            self._push()
        return result

    return deco


def commit(method):
    def deco(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        self._commit()
        return result

    return deco


class ScandResolver(ResolverBase):
    _Filename = "scand_map.json"
    _Encrypted = "map.json.enc"
    _Dir_path = os.path.dirname(os.path.realpath(__file__))
    _Repo_path = os.path.join(_Dir_path, 'encoded')
    _Repo_remote_path = 'git@github.com:cshnick/encodedp.git'
    _Filename_path = os.path.join(_Dir_path, _Filename)
    _Encrypted_path = os.path.join(_Repo_path, _Encrypted)

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
        self._remote_update = False
        self._data = {self.Pairs_tag: {}}
        self._commit_info = None

    @property
    def path(self):
        return os.path.join(self._encrypted_dir, self._encrypted_filename)

    @path.setter
    def path(self, value):
        self._encrypted_dir = os.path.dirname(value)
        self._encrypted_filename = os.path.basename(value)

    @property
    def password(self):
        return self._enc_password

    @password.setter
    def password(self, value):
        self._enc_password = value

    @property
    def remote(self):
        return self._remote

    @remote.setter
    def remote(self, value):
        self._remote = value

    @property
    def pairs(self):
        return self._data[self.Pairs_tag]

    @property
    def remote_update(self):
        return self._remote_update

    @remote_update.setter
    def remote_update(self, value):
        self._remote_update = value

    @property
    def _commit_add(self):
        return self._commit_info

    @_commit_add.setter
    def _commit_add(self, value):
        self._commit_info = value
        log.info(value)

    @pull_if_required
    def password_for_name(self, name, default=None):
        self._commit_add = "password for name %s from %s" % (name, self.path)
        password = default
        if name in self.pairs:
            password = self.pairs[name]

        return password

    @profile
    def check_password(self, chk):
        empty_dic = {ScandResolver.Pairs_tag: {}}
        old_pass, old_data = self.password, self._data
        self.password = chk
        try:
            self._load(empty_dic, io='buffer')
        except DecodeError:
            return False
        finally:
            self.password, self._data = old_pass, old_data

        return True

    @push_if_required
    @commit
    def add_password(self, key, password):
        self._commit_add = 'add; key: %s; password: %s' % (key, ''.join(['*' for x in password]))
        if not key or key in self.pairs:
            return False
        if password is None:
            password = generate_pass()
        self.pairs[key] = password
        self._save_data()
        return True

    @push_if_required
    @commit
    def set_password(self, key, password):
        self._commit_add = 'set; key: %s; password: %s' % (key, ''.join(['*' for x in password]))
        if not key or not password or not key in self.pairs:
            return False
        self.pairs[key] = password
        self._save_data()
        return True

    @push_if_required
    @commit
    def rename_key(self, old_key, new_key):
        self._commit_add = 'rename; old_key: %s; new_key: %s' % (old_key, new_key)
        if not old_key or not new_key or \
                not old_key in self.pairs or new_key in self.pairs or \
                        old_key == new_key:
            return False

        self.pairs[new_key] = self.pairs.get(old_key)
        del self.pairs[old_key]
        self._save_data()
        return True

    @push_if_required
    @commit
    def del_item(self, key):
        self._commit_add = 'delete; key: %s' % key
        if not key or not key in self.pairs:
            return False
        del self.pairs[key]
        self._save_data()
        return True

    def restore(self):
        with open(ScandResolver._Filename_path, 'rb') as scand_encrypted:
            with open(ScandResolver._Encrypted_path, 'wb') as scand_map_file:
                file_cryptor.encrypt(in_file=scand_encrypted,
                                     out_file=scand_map_file,
                                     password=b'')

    @pull_if_required
    def update(self):
        self._load_to_data()

    def _save(self, *args, **kwargs):
        with customopen(*args, **kwargs) as source_io:
            with open(self.path, "wb") as enc_dest_io:
                # fill buffer with json data
                if kwargs['io'] is 'buffer':
                    json_bytes = json.dumps(self._data).encode('utf-8')
                    source_io.write(json_bytes)
                    source_io.seek(0)

                file_cryptor.encrypt(in_file=source_io,
                                     out_file=enc_dest_io,
                                     password=self.password.encode('utf-8'))

    def _load(self, *args, **kwargs):
        try:
            with open(self.path, "rb") as enc_source_io:
                with customopen(*args, **kwargs) as destination_io:
                    try:
                        file_cryptor.decrypt(in_file=enc_source_io,
                                             out_file=destination_io,
                                             password=self.password.encode('utf-8'))

                        destination_io.seek(0)
                        decoded = destination_io.read().decode('utf-8')
                    except file_cryptor.EmptyIOError:
                        return
                    except UnicodeDecodeError:
                        raise DecodeError()

                    if not decoded:
                        raise DecodeError()
                    self._data = json.loads(decoded)
        except FileNotFoundError:
            raise RuntimeError("Suppose you've not synced to remote repo. Try using -r option")

    def _commit(self):
        if not os.path.exists(ScandResolver.RepoPath + "/.git"):
            os.makedirs(self._Repo_path, exist_ok=True)
            repo = Repo.clone_from(self._remote, self._encrypted_dir)
        else:
            repo = Repo(self._encrypted_dir)
        index = repo.index
        diff = index.diff(None)
        modified = [di.a_path or di.b_path for di in index.diff(None) if di.change_type == 'M']
        if modified:
            import datetime
            import socket
            index.add(modified)
            index.commit('%s %s- from %s'
                         % (datetime.datetime.now(),
                            '- ' + self._commit_info + ' ' if self._commit_info else '',
                            socket.gethostname()))
        return repo

    def _pull(self):
        repo = self._commit()

        class MyProgressPrinter(git.RemoteProgress):
            def update(self, op_code, cur_count, max_count=None, message=''):
                log.info("%s percents" % (cur_count / (max_count or 100.0) * 100))

        for info in repo.remotes.origin.pull(progress=MyProgressPrinter()):
            log.info("Pulled %s to %s" % (info.ref, info.commit.message))

    def _push(self):
        repo = self._commit()
        for info in repo.remotes.origin.push():
            log.info("Pushed %s" % info.local_ref.commit.message)

    def _save_data(self):
        self._save(io='buffer')

    def _save_file(self):
        self._save(ScandResolver._Filename_path, 'r', io='file')

    def _load_to_data(self):
        try:
            self._load(self._data, io='buffer')
        except DecodeError:
            pass

    def _load_from_decoded(self):
        self._load(ScandResolver._Filename_path, 'r+', io='file')
        pass
