#!/bin/bash

yakuake-session -q -t "build" --hold --workdir /home/ilia/Development/to_sort/test_curl -e 'clear' 1>/dev/null 2>/dev/null
yakuake-session -q -t "bin" --hold --workdir "/home/ilia/Development/to_sort/build-qml_currency-Desktop_Qt_5_3_GCC_64bit-Debug" -e 'clear' 1>/dev/null 2>/dev/null
yakuake-session -q -t "python bin" --hold --workdir "/home/ilia/Documents/script/python" -e 'clear' 1>/dev/null 2>/dev/null
yakuake-session -q -t "ae build" --hold --workdir "/home/ilia/Development/to_sort/Achivement_Engine/eclipse_build" -e 'clear' 1>/dev/null 2>/dev/null
yakuake-session -q -t "ae bin" --hold --workdir "/home/ilia/Development/to_sort/Achivement_Engine/eclipse_build/bin" -e 'clear' 1>/dev/null 2>/dev/null
yakuake-session -q -t "ae server" --hold --workdir "/home/ilia/Development/to_sort/Achivement_Engine/eclipse_build/bin" -e 'clear && ./tinny_http_server' 1>/dev/null 2>/dev/null
yakuake-session -q -t "ae src" --hold --workdir "/home/ilia/Development/to_sort/Achivement_Engine/engine" -e 'clear' 1>/dev/null 2>/dev/null
qdbus org.kde.yakuake /yakuake/tabs setTabTitle 0 "Start" 1>/dev/null 2>/dev/null
qdbus org.kde.yakuake /yakuake/tabs sessionAtTab 2 1>/dev/null 2>/dev/null
#sleep 10 
#reload-compositor &
