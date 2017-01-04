#!/usr/bin/python3

import sys

from PyQt5.QtCore import pyqtProperty, pyqtSlot, QObject, QUrl
from PyQt5.QtQml import qmlRegisterType, qmlRegisterUncreatableType, QQmlComponent, QQmlApplicationEngine
from PyQt5.QtGui import QGuiApplication
from cozy_password.resolver import ScandResolver
import logging as log


# This is the type that will be registered with QML.  It must be a
# sub-class of QObject.
class Resolver(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialise the value of the properties.
        self._name = 'John'
        self._shoeSize = 0
        self.__resolver = ScandResolver()


    @pyqtProperty('QString')
    def name(self):
        return self._name

    # Define the setter of the 'name' property.
    @name.setter
    def name(self, name):
        print("Incoming name: %s" % name)
        self._name = name

    @pyqtProperty('QStringList')
    def keys(self):
        log.debug('Requesting keys')
        [log.debug(k) for k in self.__resolver.data()['Pairs']]
        return [k for k in self.__resolver.data()['Pairs']]


# Create the application instance.
app = QGuiApplication(sys.argv)

qmlRegisterType(Resolver, 'PyResolver', 1, 0, 'Resolver')

engine = QQmlApplicationEngine()
engine.load(QUrl('main.qml'))

app.exec_()

if person is not None:
    # Print the value of the properties.
    print("The person's name is %s." % person.name)
    print("They wear a size %d shoe." % person.shoeSize)
else:
    # Print all errors that occurred.
    for error in component.errors():
        print(error.toString())