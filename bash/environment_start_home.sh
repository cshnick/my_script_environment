#!/bin/bash

yakuake-session -q -t "nacl" --hold --workdir /home/ilia/Development/nacl/nacl_sdk/pepper_49 -e 'clear' 1>/dev/null 2>/dev/null
yakuake-session -q -t "webports" --hold --workdir /home/ilia/Development/webports/src -e 'clear' 1>/dev/null 2>/dev/null
yakuake-session -q -t "ssh-tar" --hold --workdir /home/ilia/Development/unsorted/ssh-tar -e 'clear' 1>/dev/null 2>/dev/null 
yakuake-session -q -t "youtube-dl" --hold --workdir /home/ilia/Development/youtube-dl -e 'clear' 1>/dev/null 2>/dev/null

qdbus org.kde.yakuake /yakuake/tabs setTabTitle 0 "Start" 1>/dev/null 2>/dev/null
qdbus org.kde.yakuake /yakuake/tabs sessionAtTab 2 1>/dev/null 2>/dev/null
#bluetooth-start
#sleep 10 
#reload-compositor &
