__author__ = 'ilia'

from dbus.mainloop.glib import DBusGMainLoop
import dbus
from enum import Enum
import pycodegenerator


class Bustype(Enum):
    SESSION = 1
    SYSTEM = 2


class DBusDataController(object):
    DBUS_SERVICE_NAME = 'org.freedesktop.DBus'

    def __init__(self, bustpy=Bustype.SESSION):
        super(DBusDataController, self).__init__()
        dbus_loop = DBusGMainLoop()
        if bustpy == Bustype.SESSION:
            self._bus = dbus.SessionBus(mainloop=dbus_loop)
        else:
            self._bus = dbus.SystemBus(mainloop=dbus_loop)


    def list_buses(self):
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

    genr = pycodegenerator.PyGenerator(classname='org_kde_dbus', filename='/home/ilia/Documents/10/generator.py')
    genr.add_header()
    genr.add_footer()

    print("dc list: %s"  % bus_list)

if __name__ == "__main__":
    main()
