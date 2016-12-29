#!/usr/bin/python3

import sys

from PyQt5.QtCore import pyqtProperty, QObject, QUrl
from PyQt5.QtQml import qmlRegisterType, QQmlComponent, QQmlApplicationEngine
from PyQt5.QtGui import QGuiApplication


# This is the type that will be registered with QML.  It must be a
# sub-class of QObject.
class Resolver(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialise the value of the properties.
        self._name = ''
        self._shoeSize = 0

    # Define the getter of the 'name' property.  The C++ type of the
    # property is QString which Python will convert to and from a string.
    @pyqtProperty('QString')
    def name(self):
        return self._name

    # Define the setter of the 'name' property.
    @name.setter
    def name(self, name):
        self._name = name

    # Define the getter of the 'shoeSize' property.  The C++ type and
    # Python type of the property is int.
    @pyqtProperty(int)
    def shoeSize(self):
        return self._shoeSize

    # Define the setter of the 'shoeSize' property.
    @shoeSize.setter
    def shoeSize(self, shoeSize):
        self._shoeSize = shoeSize

    def test(self):
        print('test')


# Create the application instance.
app = QGuiApplication(sys.argv)

engine = QQmlApplicationEngine()
engine.load(QUrl('example.qml'))

app.exec_()

if person is not None:
    # Print the value of the properties.
    print("The person's name is %s." % person.name)
    print("They wear a size %d shoe." % person.shoeSize)
else:
    # Print all errors that occurred.
    for error in component.errors():
        print(error.toString())