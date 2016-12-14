#!/bin/bash

function main {
    local_mime=$(file -b --mime-type "$1")
    case $local_mime in
    inode/directory)
        case $1 in
        \.git)
            echo "Is this git?"
            ;;
        *)
            krusader-rules dbus openInDirectory "$1"
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

