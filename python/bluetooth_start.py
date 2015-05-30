__author__ = 'ilia'
import dbus
import time

sysb = dbus.SystemBus()

hci0 = sysb.get_object('org.bluez', '/org/bluez/hci0')
prop = dbus.Interface(hci0, 'org.freedesktop.DBus.Properties')

if not prop.Get('org.bluez.Adapter1', 'Powered'):
    prop.Set('org.bluez.Adapter1', 'Powered', True)
    while True:
        if prop.Get('org.bluez.Adapter1', 'Powered'):
            break
        time.sleep(0.1)
    print 'Controller powered: %s' % prop.Get('org.bluez.Adapter1', 'Powered')
else:
    print "Bluetooth controller powered"

sony = sysb.get_object('org.bluez', '/org/bluez/hci0/dev_0C_A6_94_7A_C1_93')
prop = dbus.Interface(sony, 'org.freedesktop.DBus.Properties')
sony_device = dbus.Interface(sony, 'org.bluez.Device1')

if not prop.Get('org.bluez.Device1', 'Connected'):
    sony_device.Connect()
    while True:
        if prop.Get('org.bluez.Device1', 'Connected'):
            break
        time.sleep(0.1)
    print "Controller connected: %s" % prop.Get('org.bluez.Device1', 'Connected')
else:
    print "Sony already connected"

