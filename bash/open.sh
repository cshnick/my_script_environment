#!/bin/bash

function main {
    local_mime=$(file -b --mime-type "$1")
    case $local_mime in
    inode/directory)
        case $1 in
        *\.git)
            gitkraken -d `dirname "$1"` 1>/dev/null 2>/dev/null &
            ;;
        *)
            side=1
            if [[ -n "$2" ]] ; then
                side="$2"
            fi
            krusader-rules dbus openInDirectory "$1" $side
            ;;
        esac
        ;;
    text/x-python)
        kwrite "$@"
        ;;
    *)
        /usr/bin/xdg-open "$@"
        ;;
    esac
}

main $@

