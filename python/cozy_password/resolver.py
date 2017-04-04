#!/usr/bin/env python

import json
import logging as log
import os
from os.path import realpath, join, dirname, exists
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
_PROVIDER_TAG = 'provider'
_NAME_TAG = 'name'
_REPO_NAME_TAG = 'repo_name'
_CRED_FILE_TAG = 'cred_file'
_URL_TAG = 'url'
_MERGE_PRIORITY_TAG = 'merge_priority'
_USERNAME_TAG = 'username'
_PASSWORD_TAG = 'password'
_LOCAL_VAL = 'local'
_REMOTE_VAL = 'remote'
_BITBUCKET_VAl = 'bitbucket'
_MASTER = 'master'


class ApiProviderFactory(object):
    def provider(self, name, config=None):
        if name == _BITBUCKET_VAl:
            return BBApiProvider(config)


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
        try:
            # repo exists
            repo = git.Repo(self._target_dir)
            if self._needs_upgrade():
                self._upgrade_to_remote(repo)
        except (git.InvalidGitRepositoryError, git.NoSuchPathError):
            # 1s time usagef
            repo = self._init_local()
            if self.remote_update:
                self._upgrade_to_remote(repo)

        self._handle_n_pull() if self.remote_update else self._commit()
        result = method(self, *args, **kwargs)
        self._handle_n_push() if self.remote_update else self._commit()
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


def handle_unexists(method):
    def deco(self, *args, **kwargs):
        try:
            result = method(self, *args, **kwargs)
        except git.GitCommandError as e:
            if 'not found' in str(e):  # repo not found
                self._provider_helper.create_repo()
            elif 'git pull' in str(e) and e.status == 1:
                self._empty_repo = True  # empty repository
            self._push()

            result = method(self, *args, **kwargs)
        return result

    return deco


class ScandResolver(ResolverBase):
    _ENC_FILENAME = 'map.json.enc'
    _DEFAULT_STORAGE_NAME = 'encoded'
    _PAIRS_TAG = 'Pairs'

    p_fact = ApiProviderFactory()

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
        self._provider_helper = None

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

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
        userconfig = data[_CONFIG_TAG][_USERS_TAG][self._username]
        self._merge_priority = userconfig[_REMOTE_TAG][_MERGE_PRIORITY_TAG]
        provider_name = userconfig[_REMOTE_TAG][_PROVIDER_TAG][_NAME_TAG]
        self._provider_helper = self.p_fact.provider(
            name=provider_name,
            config=userconfig)
        self._remote_url = self._provider_helper.url
        pass

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

    @push_if_required
    @commit
    def from_file(self, filename):
        try:
            with open(filename, 'r') as fp:
                pairs = json.load(fp)
                if isinstance(pairs, dict):
                    self._data[_PAIRS_TAG] = pairs
                self._save_data()
                self._commit_add = 'loaded from file'
        except (FileNotFoundError, Exception) as e:  # TODO Correct ex handling
            print('Invalid file: %s %s' % (filename, e))

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

    def _from_bytes(self, stream):
        with customopen(io='buffer') as enc_io, customopen(io='buffer') as dec_io:
            enc_io.write(stream)
            enc_io.seek(0)
            try:
                file_cryptor.decrypt(in_file=enc_io,
                                     out_file=dec_io,
                                     password=self.password.encode('utf-8'))

                dec_io.seek(0)
                decoded = dec_io.read().decode('utf-8')
                return json.loads(decoded)
            except file_cryptor.EmptyIOError:
                return
            except UnicodeDecodeError:
                raise DecodeError()

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
                self._commit_add = 'Empty pairs dict created'
                self._commit()
            else:
                raise RuntimeError("Password not set")

    def _commit(self, repo=None, initial=False):
        repo = repo or Repo(self._target_dir)
        assert repo
        index = repo.index
        modified = [di.a_path or di.b_path for di in index.diff(None) if di.change_type in ['M']]
        untracked = [file for file in repo.untracked_files if file == self._ENC_FILENAME]
        modified.extend(untracked)
        if modified or initial:
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

        for info in repo.remotes.origin.fetch(repo.references[_MASTER], progress=MyProgressPrinter()):
            log.info("Pulled %s to %s" % (info.ref, info.commit.message))

        remote_commit = repo.remotes.origin.refs.master.commit
        local_commit = repo.references[_MASTER].commit
        if local_commit != remote_commit:
            enc_bytes = (remote_commit.tree / self._ENC_FILENAME).data_stream.read()
            remote_data = self._from_bytes(enc_bytes)
            self._data.update(remote_data) if self._merge_priority == _REMOTE_VAL else remote_data.update(self._data)
            self._save_data()
            repo.index.merge_tree(repo.heads.master, base=repo.merge_base(local_commit, remote_commit))
            self._commit_add = 'Dicts changed, merged with "%s" policy' % self._merge_priority
            self._commit()

    def _push(self, repo=None):
        repo = repo or self._commit()
        for info in repo.remotes.origin.push(repo.references[_MASTER]):
            log.info("Pushed %s" % info.local_ref.commit.message)

    @handle_unexists
    def _handle_n_push(self):
        return self._push()

    @handle_unexists
    def _handle_n_pull(self):
        return self._pull()

    def _save_data(self):
        self._save(io='buffer')

    def _load_to_data(self):
        try:
            self._load(self._data, io='buffer')
        except DecodeError:
            pass

    def _init_local(self):
        os.makedirs(self._target_dir, exist_ok=True)
        if not exists(self._target_path):
            self._save_data()
        repo = git.Repo.init(self._target_dir)
        log.info('Repo init at %s' % repo.working_dir)
        return repo

    def _upgrade_to_remote(self, repo):
        repo.create_remote('origin', self._remote_url)
        log.info('origin is %s' % self._remote_url)
        self._commit_add = "Upgrade to remote"
        self._commit(repo, initial=True)
        # self._push(repo)

    def _is_local(self, repo=None):
        repo_ref = repo or git.Repo.init(self._target_dir)
        return True if not repo_ref.remotes else False

    def _needs_upgrade(self):
        return True if self._is_local() and self.remote_update else False


class ApiProviderBase(object):
    def create_repo(self):
        return False


class BBApiProvider(ApiProviderBase):
    template = 'https://%(username)s@bitbucket.org/%(username)s/%(reponame)s.git'

    def __init__(self, config: dict):
        super().__init__()
        self.username = None
        self.password = None
        self.reponame = None
        self.config = config
        self._init()

    def _init(self):
        self.reponame = self.config[_REMOTE_TAG][_PROVIDER_TAG][_REPO_NAME_TAG]
        cred_file = join(dirname(__file__), self.config[_REMOTE_TAG][_PROVIDER_TAG][_CRED_FILE_TAG])
        with open(cred_file) as crf:
            crf_config = json.load(crf)
        self.username = crf_config[_USERNAME_TAG] or None
        self.password = crf_config[_PASSWORD_TAG] or None

    @property
    def url(self):
        return self.template % {'username': self.username, 'reponame': self.reponame}

    def create_repo(self):
        from urllib.parse import urlencode
        from urllib.request import Request, urlopen
        from base64 import encodebytes
        create_url = 'https://api.bitbucket.org/1.0/repositories/'
        encoded = ('%s:%s' % (self.username, self.password)).encode('utf-8')
        user_password = encodebytes(encoded).decode('utf-8').replace('\n', '')
        headers = {'Authorization': 'Basic %s' % user_password,
                   'Content-Type': 'application/x-www-form-urlencoded'}
        values = {'name': self.reponame,
                  'is_private': 'true'}
        data = urlencode(values).encode('utf-8')
        req = Request(create_url, data, headers)
        reply = urlopen(req).read().decode('utf-8')
        log.info('Reply result %s' % reply)
        return json.loads(reply)['is_private']
