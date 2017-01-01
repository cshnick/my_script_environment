#!/bin/bash

yakuake-session -q -t "Development" --hold --workdir /home/ilia/Development -e 'clear' 1>/dev/null 2>/dev/null
yakuake-session -q -t "CMServer" --hold --workdir /home/ilia/Development/scand/communication_model/NcConsole/cmake-Poco/bin -e 'clear' 1>/dev/null 2>/dev/null
yakuake-session -q -t "CMClient" --hold --workdir /home/ilia/Development/scand/communication_model/NcConsole/cmake-Poco/bin -e 'clear' 1>/dev/null 2>/dev/null
yakuake-session -q -t "CMBuild" --hold --workdir /home/ilia/Development/scand/communication_model/NcConsole/cmake-Poco -e 'clear' 1>/dev/null 2>/dev/null
#yakuake-session -q -t "webports" --hold --workdir /home/ilia/Development/webports/src -e 'clear' 1>/dev/null 2>/dev/null
#yakuake-session -q -t "ssh-tar" --hold --workdir /home/ilia/Development/unsorted/ssh-tar -e 'clear' 1>/dev/null 2>/dev/null 
#yakuake-session -q -t "youtube-dl" --hold --workdir /home/ilia/Development/youtube-dl -e 'clear' 1>/dev/null 2>/dev/null

qdbus org.kde.yakuake /yakuake/tabs setTabTitle 0 "Start" 1>/dev/null 2>/dev/null
qdbus org.kde.yakuake /yakuake/tabs sessionAtTab 2 1>/dev/null 2>/dev/null

xhost +
#bluetooth-start
#sleep 10 
#reload-compositor &
