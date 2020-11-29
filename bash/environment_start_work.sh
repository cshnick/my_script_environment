# !bin/bash

#PROGNOZ
#yakuake-session -q -t "build64" --hold --workdir /home/ilia/Prognoz/P7/DEV8/build64 -e 'export CPLUS_INCLUDE_PATH=/usr/lib64/glib-2.0/include:/opt/gcc471/include PATH=/opt/gcc471/bin:$PATH LD_LIBRARY_PATH=/opt/gcc471/lib64:$LD_LIBRARY_PATH && clear' 1>/dev/null 2>/dev/null  
#yakuake-session -q -t "bin" --hold --workdir /home/ilia/Prognoz/P7/DEV8/build64/bin -e 'clear' >/dev/null
#yakuake-session -q -t "build32" --hold --workdir /home/ilia/Prognoz/P7/DEV8/build32 -e 'export CPLUS_INCLUDE_PATH=/usr/lib64/glib-2.0/include:/opt/gcc471/include PATH=/opt/gcc471/bin:$PATH LD_LIBRARY_PATH=/opt/gcc471/lib:$LD_LIBRARY_PATH     && clear' 1>/dev/null 2>/dev/null
#yakuake-session -q -t "bin32" --hold --workdir /home/ilia/Prognoz/P7/DEV8/build32/bin -e 'clear' >/dev/null
#PROGNOZ

#yakuake-session -q -t "sm src" --hold --workdir /home/ilia/Development/sm_service_model -e 'clear' >/dev/null
#yakuake-session -q -t "sm build" --hold --workdir /home/ilia/Development/cmake_sm -e 'clear' >/dev/null

#yakuake-session -q -t "nacl" --hold --workdir /home/ilia/Development/nacl/nacl_sdk/pepper_47 -e 'clear' >/dev/null
#yakuake-session -q -t "nacl ports" --hold --workdir /home/ilia/Development/nacl/webports_gclient -e 'clear' >/dev/null

#yakuake-session -q -t "POCO Server" --hold --workdir /home/ilia/Development/nacl/nc-ui-prototype/NcConsole/cmake-Poco/bin -e 'clear' >/dev/null
#yakuake-session -q -t "POCO Client" --hold --workdir /home/ilia/Development/nacl/nc-ui-prototype/NcConsole/cmake-Poco/bin -e 'clear' >/dev/null

#qdbus org.kde.yakuake /yakuake/tabs setTabTitle 0 "Start" 1>/dev/null 2>/dev/null
#qdbus org.kde.yakuake /yakuake/tabs sessionAtTab 2 1>/dev/null 2>/dev/null

klipper


#krusader 1>/dev/null 2>/dev/null &
#thunderbird 1>/dev/null 2>/dev/null &

#cat $HOME/.Skype/login_luxa_ryabic | skype --enable-dbus --use-system-dbus --pipelogin 1>/dev/null 2>/dev/null &
#cat $HOME/.Skype/login_sc.ilin.ivan | skype --pipelogin &
#cat $HOME/.Skype/login_sc.ryabokon.ilia | skype --pipelogin 1>/dev/null 2>/dev/null &
