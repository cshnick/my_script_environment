#!/bin/bash
#
# yakuake-session - A script to create new yakuake sessions from command-line.
#
# Copyright 2010-2013 Jesús Torres <aplatanado@gulic.org>
#
# yakuake-session comes with ABSOLUTELY NO WARRANTY; for details see COPYING.
# This is free software, and you are welcome to redistribute it
# under certain conditions; see COPYING for details.
#

type -P yakuake &> /dev/null
if [ "$?" != 0 ]; then
  echo "$(basename $0): error: yakuake is not installed" 1>&2
  exit 5
fi

function getcomm {
  type -P qdbus &> /dev/null && \
    qdbus 2> /dev/null | grep -q org.kde.yakuake
  if [[ "$?" == 0 ]]; then
    echo dbus
    return
  fi
  type -P dcop &> /dev/null && \
    dcop 2> /dev/null | grep -q yakuake
  if [[ "$?" == 0 ]]; then
    echo dcop
    return
  fi
  echo none
}

#
# DBUS

function dbus_addsession {
  qdbus org.kde.yakuake /yakuake/sessions addSession > /dev/null
}

function dbus_runcommand {
  qdbus org.kde.yakuake /yakuake/sessions runCommand "$1" > /dev/null
}

function dbus_hasinterface {
  qdbus org.kde.yakuake /yakuake/MainWindow_1 Introspect | grep -F "<interface name=\"$1\">"
}

function dbus_settitle {
  id=$(qdbus org.kde.yakuake /yakuake/sessions sessionIdList | tr , "\n" | sort -g | tail -1 | tr -d '\n')
  qdbus org.kde.yakuake /yakuake/tabs setTabTitle "$id" "$1" 
}

function dbus_showwindow {
  #if [[ $? -eq 0 ]]; then
  #  interface="com.trolltech.Qt.QWidget"
  #else
    interface="org.qtproject.Qt.QWidget"
  #fi
  ws=$(qdbus org.kde.yakuake /yakuake/MainWindow_1 Get $interface visible)
  echo $ws
  if [[ $? -eq 0 && "$ws" == "false" ]]; then
    qdbus org.kde.yakuake /yakuake/window toggleWindowState > /dev/null
  fi
}

#
# DCOP

function dcop_settitle {
  echo "$(basename $0): warning: set tab title is not yet supported when using DCOP interface" 1>&2
}

function dcop_addsession {
  dcop yakuake DCOPInterface slotAddSession > /dev/null
}

function dcop_runcommand {
  dcop yakuake DCOPInterface slotRunCommandInSession "$1" > /dev/null
}

function dcop_showwindow {
  ws=$(dcop yakuake yakuake-mainwindow#1 visible)
  if [[ "$?" == 0 && "$ws" == false ]]; then
    dcop yakuake DCOPInterface slotToggleState > /dev/null
  fi
}

hold=0
now=1
props=''
pwd="$PWD"

function addprops {
  if [[ -z "$props" ]]; then
    props="$1"
  else
    props="$props,$1"
  fi
}

function showhelp {
  cat <<EOF

Usage: $(basename $0) [options] [args]

Options:
  --help                    Show help about options.
  -h, --homedir             Set the working directory of the new tab to the user's home.
  -w, --workdir <dir>       Set the working directory of the new tab to 'dir'
  --hold, --noclose         Do not close the session automatically when the command ends.
  -p <property=value>       Change the value of a profile property (only for KDE 4).
  -e <cmd>                  Command to execute.
  -q                        Do not open yakuake window.
  -t <title>                Set the title of the new tab

Arguments:
  args                      Arguments passed to command.
EOF
}

opts=$(getopt -n $(basename $0) -o t:e:p:w:hq \
       -l workdir:,hold,noclose,help -- "$@")
eval set -- "$opts"
while true; do
  case "$1" in
    --help) showhelp; exit 0 ;;
    -w|--workdir) pwd="$2"; shift 2 ;;
    --hold|--noclose) hold=1; shift ;;
    -p) addprops "$2"; shift 2 ;;
    -e) cmd="$2"; shift 2 ;;
    -t) title="$2"; shift 2 ;;
    -h|--homedir) pwd=''; shift ;;
    -q) now=0; shift ;;
    --) shift; break ;;
    *) echo "$(basename $0): internal error" 1>&2; exit 1 ;;
  esac
done
for arg do args="$args '$arg'" ; done

comm=$(getcomm)
if [[ "$comm" == none ]]; then
  yakuake || exit 2
  comm=$(getcomm)
  if [[ "$comm" == none ]]; then
    exit 3
  fi
fi

${comm}_addsession > /dev/null || exit 4
if [[ -n "$props" ]]; then
  type -P konsoleprofile &> /dev/null && \
    ${comm}_runcommand "konsoleprofile '$props'" || exit 4
fi
if [[ -n "$pwd" ]]; then
  ${comm}_runcommand "cd '$pwd'" || exit 4
fi
if [[ -n "$cmd" ]]; then
#  if type -p "$cmd" &> /dev/null; then
    if [[ "$hold" == 1 ]]; then
      ${comm}_runcommand "$cmd" || exit 4
    else
      ${comm}_runcommand "exec $cmd" || exit 4
    fi
#  else
#    exit 3
#  fi
fi
if [[ -n "$title" ]]; then
  ${comm}_settitle "$title"
fi
if [[ "$now" == 1 ]]; then
  ${comm}_showwindow
fi
