#!/bin/bash

function ifdebug {
    if [[ -n $DEBUG ]] ; then
        $@
    fi
}

function invert {
    if [[ $1 == "0" ]] ; then
        echo "1"
    else
        echo "0"
    fi
}

function main {
    local_mime=$(file -b --mime-type "$1")
    case $local_mime in
    inode/directory)
        case $1 in
        *\.git)
            ifdebug echo "openning git gui for "$(dirname $(realpath "$1"))
            smartgit "$(dirname $(realpath $1))" 1>/dev/null 2>/dev/null &
            ;;
        *)
            side=1
            tmp_latest_tab="/tmp/.opensh/tab"
            if [[ -n "$2" ]] ; then
                side="$2"
            elif [[ -f "$tmp_latest_tab" ]] ; then
                side=$(cat "$tmp_latest_tab")
            fi
            krusader-rules dbus openInDirectory "$1" $side
            mkdir -p $(dirname "$tmp_latest_tab")
            invert $side > "$tmp_latest_tab"
            ;;
        esac
        ;;
    text/x-python)
        kwrite "$@"
        ;;
    *)
        if [[ ${1: -3} == ".sh" ]] ; then
            kwrite $(realpath "$1") 1>/dev/null 2>/dev/null &
        else
            /usr/bin/xdg-open "$@"
        fi
        ;;
    esac
}

main $@