#!/usr/bin/python3

import sys

from PyQt5.QtCore import pyqtProperty, pyqtSlot, QObject, QUrl
from PyQt5.QtQml import qmlRegisterType, qmlRegisterUncreatableType, QQmlComponent, QQmlApplicationEngine
from PyQt5.QtGui import QGuiApplication
from cozy_password.resolver import ScandResolver
import logging as log
import pyperclip as clip
from cozy_password.QSingleApplication import QtSingleGuiApplication
import socket, os

# This is the type that will be registered with QML.  It must be a
# sub-class of QObject.
class Resolver(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__resolver = ScandResolver()

    @pyqtProperty('QStringList')
    def keys(self):
        log.debug('Requesting keys')
        # [log.debug(k) for k in self.__resolver.data()['Pairs']]
        return [k for k in self.__resolver.data()['Pairs']]

    # Key 2 password
    @pyqtSlot(str)
    def k2p_clipboard(self, arg):
        if not arg:
            return
        password = self.__resolver.password_for_name(arg)
        clip.copy(password)

    @pyqtSlot(str, str)
    def new_entry(self, key, password):
        pass


from contextlib import contextmanager
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
    engine.load(QUrl('main.qml'))
    mwn = engine.rootObjects()[0]
    app.setActivationWindow(mwn)
    mwn.hide()

    sys.exit(app.exec_())
