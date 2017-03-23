#/bin/bash

with_log() {
    if [[ -n $DEBUG ]] ; then
        echo "$@" 
    fi
    $@
}

realpwd=$(dirname $(readlink $0))
pyscript_dir=$(realpath $realpwd/../python/cozy_password)

with_log cd $pyscript_dir
with_log python3 ./resolver_qt.py
