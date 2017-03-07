#!/bin/bash

#yakuake-session -q -t "Development" --workdir /home/ilia/Development -e 'clear' --hold & #1>/dev/null 2>/dev/null
#yakuake-session -q -t "CMServer" --workdir /home/ilia/Development/scand/communication_model/NcConsole/cmake-Poco/bin -e 'clear' --hold & #1>/dev/null 2>/dev/null
#yakuake-session -q -t "CMClient" --workdir /home/ilia/Development/scand/communication_model/NcConsole/cmake-Poco/bin -e 'clear' --hold & #1>/dev/null 2>/dev/null &
#yakuake-session -q -t "CMBuild" --workdir /home/ilia/Development/scand/communication_model/NcConsole/cmake-Poco -e 'clear' --hold & #1>/dev/null 2>/dev/null &
#yakuake-session -q -t "webports" --hold --workdir /home/ilia/Development/webports/src -e 'clear' 1>/dev/null 2>/dev/null
#yakuake-session -q -t "ssh-tar" --hold --workdir /home/ilia/Development/unsorted/ssh-tar -e 'clear' 1>/dev/null 2>/dev/null 
#yakuake-session -q -t "youtube-dl" --hold --workdir /home/ilia/Development/youtube-dl -e 'clear' 1>/dev/null 2>/dev/null

#qdbus org.kde.yakuake /yakuake/tabs setTabTitle 0 "Start" & #1>/dev/null 2>/dev/null &
#qdbus org.kde.yakuake /yakuake/tabs sessionAtTab 2 & #1>/dev/null 2>/dev/null &

xhost +
xinput set-prop 9 285 -0.5
#bluetooth-start
#sleep 10 
#reload-compositor &
