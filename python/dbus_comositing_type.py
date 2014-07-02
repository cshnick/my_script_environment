#!/usr/bin/python

import dbus

sb = dbus.SessionBus()

proxy = sb.get_object('org.kde.kwin.Compositing', '/Compositor')
pm = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')
pm.Set('org.kde.kwin.Compositing', 'compositingType', 'xrender')
print pm.Get('org.kde.kwin.Compositing', 'compositingType')

