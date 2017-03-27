#!/usr/bin/env python

import os
import os.path as osp
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

_SELF_PWD = os.path.realpath(__file__)
_PAIRS_TAG = 'Pairs'


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
    _ENC_FILENAME = 'map.json.enc'
    _DEFAULT_STORAGE_NAME = 'encoded'
    _PAIRS_TAG = "Pairs"

    def __init__(self):
        """ Create resolver with empty data.
            Loading process is controled by user

        """
        super().__init__()
        self._username = ''
        self._remote_url = ''
        self._target_file = self._ENC_FILENAME
        self._storage = osp.join(_SELF_PWD, self._DEFAULT_STORAGE_NAME)
        self._enc_password = ''
        self._remote_update = False
        self._data = {_PAIRS_TAG: {}}
        self._commit_info = None

    @property
    def password(self):
        return self._enc_password

    @password.setter
    def password(self, value):
        self._enc_password = value

    @property
    def remote_url(self):
        return self._remote_url

    @remote_url.setter
    def remote_url(self, value):
        self._remote_url = value

    @property
    def storage(self):
        return self._storage

    @storage.setter
    def storage(self, value):
        self._storage = value
        self._enc_password = ''

    @property
    def pairs(self):
        return self._data[_PAIRS_TAG]

    @property
    def remote_update(self):
        return self._remote_update

    @remote_update.setter
    def remote_update(self, value):
        self._remote_update = value

    @property
    def _target_path(self):
        return os.path.join(self._storage, self._username, self._target_file)

    @property
    def _target_dir(self):
        return os.path.join(self._storage, self._username)

    @property
    def _commit_add(self):
        return self._commit_info

    @_commit_add.setter
    def _commit_add(self, value):
        self._commit_info = value
        log.info(value)

    @pull_if_required
    def password_for_name(self, name, default=None):
        self._commit_add = "password for name %s" % name
        password = default
        if name in self.pairs:
            password = self.pairs[name]

        return password

    @profile
    def check_password(self, chk):
        empty_dic = {_PAIRS_TAG: {}}
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
        self._commit_add = 'add; key: %s; password: %s' % (key, ''.join(['*' for _ in password]))
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

    @pull_if_required
    def update(self):
        self._load_to_data()

    def _save(self, *args, **kwargs):
        with customopen(*args, **kwargs) as source_io:
            with open(self._target_path, "wb") as enc_dest_io:
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
            with open(self._target_path, "rb") as enc_source_io:
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
        os.makedirs(self._target_dir, exist_ok=True)
        if not os.path.exists(ScandResolver._target_dir + "/.git"):
            repo = Repo.clone_from(self._remote_url, self._target_dir)
        else:
            repo = Repo(self._target_dir)
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

    def _load_to_data(self):
        try:
            self._load(self._data, io='buffer')
        except DecodeError:
            pass
