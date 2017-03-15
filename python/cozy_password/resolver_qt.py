#!/usr/bin/python3

import sys

from PyQt5.QtCore import pyqtProperty, pyqtSlot, QObject, QUrl
from PyQt5.QtQml import qmlRegisterType, QQmlApplicationEngine
from cozy_password.resolver import ScandResolver, profile
import logging as log
import pyperclip as clip
from cozy_password.QSingleApplication import QtSingleGuiApplication
from contextlib import contextmanager


class Resolver(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._resolver = ScandResolver()

    @pyqtProperty('QStringList')
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

    @pyqtSlot(str, str)
    def new_entry(self, key, password):
        self._resolver.add_password(key, password)

    @pyqtSlot(str, result=bool)
    def check_password(self, key):
        return self._resolver.check_password(key)

    @pyqtSlot(str, result=bool)
    def contains(self, key):
        return key in self._resolver.pairs or False

    @pyqtSlot()
    def sync(self):
        self._resolver.remote_update = True
        import time
        time_ = time.time()
        self._resolver.update()
        diff = time.time() - time_
        log.debug("update last: %s" % diff)
        self._resolver.remote_update = False


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
    mwn.show()
    sys.exit(app.exec_())
