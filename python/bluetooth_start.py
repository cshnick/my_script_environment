#!/usr/bin/python

__author__ = 'ilia'
import dbus
import dbus.service
import time
import notifier
from dbus.mainloop.glib import DBusGMainLoop
import gobject


class BluezConnector(object):
    Properties = 'org.freedesktop.DBus.Properties'
    Bluez = 'org.bluez'

    def __init__(self, bus=None):
        self.__dbus = bus

    def power_on(self):
        hci0 = self.__dbus.get_object(BluezConnector.Bluez, '/org/bluez/hci0')
        __prop = dbus.Interface(hci0, BluezConnector.Properties)

        if not __prop.Get('org.bluez.Adapter1', 'Powered'):
            __prop.Set('org.bluez.Adapter1', 'Powered', True)
            while True:
                if __prop.Get('org.bluez.Adapter1', 'Powered'):
                    break
                time.sleep(0.1)
            print 'Controller powered: %s' % __prop.Get('org.bluez.Adapter1', 'Powered')
        else:
            print "Bluetooth controller powered"

    def attempt_connect_device(self):
        __sony = self.__dbus.get_object(BluezConnector.Bluez, '/org/bluez/hci0/dev_0C_A6_94_7A_C1_93')
        __prop = dbus.Interface(__sony, 'org.freedesktop.DBus.Properties')
        __sony_device = dbus.Interface(__sony, 'org.bluez.Device1')

        if not __prop.Get('org.bluez.Device1', 'Connected'):
            print "Attempting to connect sony device"
            try:
                __sony_device.Connect()
            except dbus.exceptions.DBusException as e:
                messg = "Can't connect to sony speaker; check if it had been switched on."
                print messg
                notifier.send_message(title='Sony speaker connection report', message=messg)
            except Exception as e:
                messg = "Uncaught exception: %s" % e
                print messg
                notifier.send_message(title='Sony speaker connection report', message=messg)
            if __prop.Get('org.bluez.Device1', 'Connected'):
                notifier.send_message("Sony connected", "Sony bluetooth speakers successfullly connected")
        else:
            print "Sony already connected"

    def connect_property_changed(self):
        __sony = self.__dbus.get_object(BluezConnector.Bluez, '/org/bluez/hci0/dev_0C_A6_94_7A_C1_93')
        __prop = dbus.Interface(__sony, BluezConnector.Properties)

        def __handler(*args, **kwargs):
            interface = args[0]
            data_dict = args[1]
            dbs_arr = args[2]

            print 'Signal received. Connection status: %s' % data_dict['Connected']
            self.attempt_connect_device()

        __prop.connect_to_signal("PropertiesChanged", __handler)


if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    sysb = dbus.SystemBus()
    b = BluezConnector(bus=sysb)
    b.power_on()
    b.connect_property_changed()
    # The signal is not emitted if the device is up on the boot
    b.attempt_connect_device()

    mainloop = gobject.MainLoop()
    print "Running sony speaker discovery service."
    mainloop.run()



