#!/usr/bin/python

#imports
import gobject
gobject.threads_init()
from dbus import glib
glib.init_threads()
import dbus
s_bus = dbus.SessionBus()
import time

KWin = s_bus.get_object("org.kde.kwin.Compositing", "/KWin")
kwin = dbus.Interface(KWin, "org.kde.KWin")
kwin.reconfigure()
time.sleep(1)

compositor = s_bus.get_object("org.kde.kwin.Compositing", "/Compositor")
compositing = dbus.Interface(compositor, 'org.kde.kwin.Compositing')

compositing.suspend()
compositing.resume()

kwin.reconfigure()


