#!/usr/bin/env python

import json
import logging as log
import os
from os.path import realpath, join, dirname
import time
from contextlib import contextmanager
from io import BytesIO

import git
from git import Repo

import cozy_password.file_cryptor as file_cryptor
from cozy_password.password_generator import generate_pass

log.basicConfig(level=log.INFO if 'DEBUG' in os.environ else log.WARNING,
                format='%(asctime)s - %(levelname)s - %(message)s')

_SELF_PWD = dirname(realpath(__file__))
_PAIRS_TAG = 'Pairs'
_CONFIG_TAG = 'configuration'
_DEF_USER_TAG = 'default_user'
_USERS_TAG = 'users'
_REMOTE_TAG = 'remote'
_URL_TAG = 'url'
_MERGE_PRIORITY_TAG = 'merge_priority'
_LOCAL_VAL = 'local'
_REMOTE_VAL = 'remote'
_MASTER = 'master'


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


def sync_repo(method):
    def deco(self, *args, **kwargs):
        branch = 'master'
        repo_path = self._target_dir
        try:
            repo = git.Repo(repo_path)
            if self._is_local(repo) and self._remote_update:
                self._make_remote_repo()
            elif self._remote_update:
                repo.remotes.origin.pull()
                repo.remotes.origin.push()
            log.info('Init repo, repo exists')
        except (git.InvalidGitRepositoryError, git.NoSuchPathError):
            os.makedirs(self._target_dir, exist_ok=True)
            self._make_remote_repo() if self._remote_update else self._make_local_repo()
        result = method(self, *args, **kwargs)
        return result

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
    _PAIRS_TAG = 'Pairs'

    def __init__(self):
        """ Create resolver with empty data.
            Loading process is controled by user

        """
        super().__init__()
        self._username = ''
        self._remote_url = ''
        self._target_file = self._ENC_FILENAME
        self._storage = join(_SELF_PWD, self._DEFAULT_STORAGE_NAME)
        self._enc_password = ''
        self._remote_update = False
        self._data = {_PAIRS_TAG: {}}
        self._commit_info = None
        self._merge_priority = None

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

    def read_config(self):
        config_path = __file__.replace('.py', '.json')
        with open(config_path, 'r') as cf:
            data = json.load(cf)
        self._username = data[_CONFIG_TAG][_DEF_USER_TAG]
        self.remote_url = data[_CONFIG_TAG][_USERS_TAG][self._username][_REMOTE_TAG][_URL_TAG]
        self._merge_priority = data[_CONFIG_TAG][_USERS_TAG][self._username][_REMOTE_TAG][_MERGE_PRIORITY_TAG]

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
        self._commit_add = 'set; key: %s; password: %s' % (key, ''.join(['*' for _ in password]))
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

    @sync_repo
    def update(self):
        self._load_to_data()

    def _save(self, *args, **kwargs):
        os.makedirs(self._target_dir, exist_ok=True)
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
            if self.password:
                self._save_data()
                self._commit_add = 'initial_commit'
                index = Repo(self._target_dir).index
                index.add([self._ENC_FILENAME])
                index.commit("Initial commit; %s created" % self._ENC_FILENAME)
            else:
                raise RuntimeError("Password not set")

    def _commit(self):
        repo = Repo(self._target_dir)
        assert repo
        index = repo.index
        modified = [di.a_path or di.b_path for di in index.diff(None) if di.change_type in ['M']]
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

    def _make_local_repo(self):
        repo = git.Repo.init(self._target_dir)
        log.info('Created local repository')
        return repo

    def _make_remote_repo(self):
        branch = _MASTER
        repo = git.Repo.init(self._target_dir)
        origin = repo.create_remote('origin', self._remote_url)
        origin.fetch()

        if self._merge_priority == _LOCAL_VAL:
            commit1 = repo.remotes.origin.refs.master.commit
            commit2 = repo.head.commit
            if commit1 != commit2:
                merge_base = repo.merge_base(commit1, commit2)
                repo.index.merge_tree(repo.head, base=merge_base).commit('Merge')

        master = repo.create_head(branch, origin.refs[branch], force=True)
        master.set_tracking_branch(origin.refs[branch])
        master.checkout()

        origin.pull()
        origin.push()
        return repo

    def _is_local(self, repo=None):
        repo_ref = repo or git.Repo.init(self._target_dir)
        return True if not repo_ref.remotes else False
