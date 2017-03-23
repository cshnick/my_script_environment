#!/usr/bin/python3

import sys
from PyQt5.QtCore import pyqtProperty, pyqtSignal, pyqtSlot, QObject, QUrl
from PyQt5.QtQml import qmlRegisterType, QQmlApplicationEngine
from cozy_password.resolver import ScandResolver
import logging as log
import pyperclip as clip
from cozy_password.QSingleApplication import QtSingleGuiApplication
from contextlib import contextmanager
from threading import Thread
from functools import wraps


def run_async(func):
    @wraps(func)
    def async_func(*args, **kwargs):
        func_hl = Thread(target=func, args=args, kwargs=kwargs)
        func_hl.start()
        return func_hl

    return async_func


class Resolver(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._resolver = ScandResolver()
        self._async_pending = False

    @run_async
    def _update_async(self):
        with self.remote_update():
            self._resolver.update()
        self.keys_changed.emit(list(self._resolver.pairs))

    @contextmanager
    def remote_update(self):
        store = self._resolver.remote_update
        self._resolver.remote_update = True
        try:
            yield
        finally:
            self._resolver.remote_update = store

    keys_changed = pyqtSignal('QStringList', name='keysChanged', arguments=['newkeys'])
    async_pending_changed = pyqtSignal(bool, name='asyncPendingChanged', arguments=['pending'])
    password_changed = pyqtSignal(str)

    @pyqtProperty(str)
    def password(self):
        return self._resolver.password

    @password.setter
    def password(self, value):
        self._resolver.password = value
        self.password_changed.emit(value)

    @pyqtProperty(str, notify=async_pending_changed)
    def async_pending(self):
        return self._async_pending

    @async_pending.setter
    def async_pending(self, value):
        self._async_pending = value

    @pyqtProperty('QStringList', notify=keys_changed)
    def keys(self):
        log.log(log.NOTSET, 'Requesting keys')
        return list(self._resolver.pairs)

    # Key 2 password
    @pyqtSlot(str)
    def k2p_clipboard(self, arg):
        if not arg:
            return
        password = self._resolver.password_for_name(arg)
        if password:
            clip.copy(password)

    @pyqtSlot(str, str, result=bool)
    def new_entry(self, key, password):
        with self.remote_update():
            return self._resolver.add_password(key, password)

    @pyqtSlot(str, str, result=bool)
    def set(self, key, password):
        with self.remote_update():
            return self._resolver.set_password(key, password)

    @pyqtSlot(str, result=bool, name='del')
    def del_(self, key):
        with self.remote_update():
            return self._resolver.del_item(key)

    @pyqtSlot(str, result=bool)
    def check_password(self, key):
        return self._resolver.check_password(key)

    @pyqtSlot(str, result=bool)
    def contains(self, key):
        return key in self._resolver.pairs or False

    @pyqtSlot()
    def sync(self):
        self._update_async()


@contextmanager
def open_single_application(*args):
    qtapp = QtSingleGuiApplication(*args)
    try:
        yield qtapp
    finally:
        qtapp.stop()


appGuid = '54022365-9923-4ba5-a589-c9dfca2326de'
with open_single_application(appGuid, sys.argv) as app:
    if app.isRunning(): sys.exit(0)

    qmlRegisterType(Resolver, 'PyResolver', 1, 0, 'Resolver')
    engine = QQmlApplicationEngine()
    engine.load(QUrl('cpass_gui/main.qml'))
    mwn = engine.rootObjects()[0]
    app.setActivationWindow(mwn)
    mwn.hide()
    sys.exit(app.exec_())
