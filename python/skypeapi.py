#!/usr/bin/env python
################################################################################
"""
   Send DBus commands to Skype.
   Inspired by http://atamanenko.blogspot.com

   @author Vadzim Struk
   @e-mail vadim.struk@gmail.com

   29 May 2013
"""
################################################################################

import sys
import dbus

################################################################################


def exec_skype_commands(commands):
    if len(commands) == 0:
        return []

    remote_bus = dbus.SessionBus()

    try:
        skype_service = remote_bus.get_object('com.Skype.API', '/com/Skype')
    except:
        raise Exception('Skype is not running')

    answer = skype_service.Invoke('NAME PythonSkypeAPI')

    if answer != 'OK':
        raise Exception('Could not bind to Skype client: %s' % answer)

    answer = skype_service.Invoke('PROTOCOL 5')

    if answer != 'PROTOCOL 5':
        raise Exception('Skype API protocol "%s" is not supported' % answer)

    answers = []

    for cmd in commands:
        answer = skype_service.Invoke(cmd)
        answers.append(answer)
        print cmd, ':', answer

    return answers


def open_unread_chats(first_only):
    answer = exec_skype_commands(['SEARCH MISSEDCHATS'])[0]

    if not answer.startswith('CHATS '):
        raise Exception('Failed to get unread chats')
    chats = [chat for chat in answer[6:].split(', ') if len(chat)]

    if first_only:
        chats = chats[:1]

    exec_skype_commands(['OPEN CHAT ' + chat for chat in chats])

    return chats

################################################################################

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print 'Usage: skypeapi.py command [command ...]'
        print '   or: skypeapi.py --open-unread-first'
        print '   or: skypeapi.py --open-unread-all'
        sys.exit(1)

    try:
        if sys.argv[1] == '--open-unread-first':
            open_unread_chats(True)
        elif sys.argv[1] == '--open-unread-all':
            open_unread_chats(False)
        else:
            exec_skype_commands(sys.argv[1:])
    except Exception, e:
        print 'ERROR:', e
        sys.exit(2)
