__author__ = 'ilia'

from dbus.mainloop.glib import DBusGMainLoop
import dbus
from enum import Enum
import codegen
import os.path as path
import sys


class Bustype(Enum):
    SESSION = 1
    SYSTEM = 2

class DBusDataController(object):
    DBUS_SERVICE_NAME = 'org.freedesktop.DBus'
    GEN_MODULE_NAME='fancybus'

    def __init__(self, bustpy=Bustype.SESSION):
        super(DBusDataController, self).__init__()
        dbus_loop = DBusGMainLoop()
        if bustpy == Bustype.SESSION:
            self._bus = dbus.SessionBus(mainloop=dbus_loop)
        else:
            self._bus = dbus.SystemBus(mainloop=dbus_loop)


    def list_buses(self):
        """
        list all buss names
        Returns:
            bus_list: list
        """
        try:
            bus_list = self._bus.list_activatable_names()
        except:
            pass
        return bus_list

def main():
    dc = DBusDataController()
    bus_list = dc.list_buses()

    thbus = dbus.SessionBus()
    proxy = thbus.get_object(DBusDataController.DBUS_SERVICE_NAME, '/')
    iface = dbus.Interface(proxy, DBusDataController.DBUS_SERVICE_NAME)
    names = iface.ListNames()

    mfullpath = path.dirname(sys.argv[0])
    modgen = codegen.PyModuleGenerator(filepath=mfullpath, name=DBusDataController.GEN_MODULE_NAME)
    modgen.generate()


    classfullpath = mfullpath + '/' + DBusDataController.GEN_MODULE_NAME
    class1 = codegen.PyClassGenerator(classname='org_kde_dbus')

    def gen_class_generator(name):
        name = name.replace('.', '_')

        return codegen.PyClassGenerator(classname=name)

    session_classes = map(gen_class_generator, dc.list_buses())

    srcgen = codegen.PySrcFileGenerator(paths=[classfullpath + '/session.py'])
    map(lambda cls: srcgen.add_class(classgenerator=cls), session_classes)
    srcgen.write()

    print("dc list: %s"  % bus_list)

if __name__ == "__main__":
    main()
