import dbus

class IfaceGenetator(object):
    DEFAULt_FILEFORMAT = '%s.py'

    def __init__(self, iface_name, dbusobj=None):
        if not dbusobj:
            self.dbusobj = dbus.SessionBus()

        assert(self._check_iface(iface_name))
        self._iface_name = iface_name

    def generate(self, file=None):
        if not file:
            filename = IfaceGenetator.DEFAULt_FILEFORMAT % self._iface_name
            file = open(filename, 'w')



    def _check_iface(self, ifacename):
        #proxy = self.dbusobj.
        print(dbus.validate_interface_name(ifacename))
        return False


#For tests
def main():
    #gen = IfaceGenetator('org.freedesktop.DBus')
    bus = dbus.SessionBus()
    proxy = bus.get_object(dbus.BUS_DAEMON_IFACE, '/')
    print('table: %s' % proxy)

    pass

if __name__ == '__main__':
    main()





