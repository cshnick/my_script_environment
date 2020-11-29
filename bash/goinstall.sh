#!/bin/bash 

function log() {
  echo "$@"
  $@
}

function blocking_warning() {
  local message="$1"
  read -p "$message" -n 1 -r
  echo
}


# Takes a string version from filename
function infer_version() {
  local archive_string="$1"
  echo ${archive_string#go} | cut -d'.' -f 1,2,3 --output-delimiter='.' 
}

#checks if uid of parameter is 0
function rootreq() {
  local filepath="$1"
  case $(stat -c %u "$filepath") in
    0) echo true ;;
    *) echo false ;;
  esac
}

function delete_dir_if_exists() {
  local delete_path="$1"
  [ ! -e $delete_path ] && return
  [ ! -d $delete_path ] && echo "Warning, you're deleting $delete_path which is not a directory" && return
  blocking_warning "$delete_path will be deleted, press enter to confirm"
  cmd="rm -rf $delete_path"
  [ $(rootreq "$delete_path") == true ] && cmd="sudo $cmd"
  log $cmd
}

#extract golang archive to the destination
function extract_go() {
  delete_dir_if_exists "$INSTALL_PATH/$INSTALL_NAME"
  local cmd_pool=(
    "mkdir -p $INSTALL_PATH"
    "tar -C $INSTALL_PATH -xzf go1.15.5.linux-amd64.tar.gz"   
  )
  for cmd in "${cmd_pool[@]}" ; do
    [ $(rootreq "$INSTALL_PATH") == true ] && cmd="sudo $cmd"
    log $cmd
  done
}

function add_environment() {
  local profiled="/etc/profile.d/go_manual_installation.sh"
  [ $(rootreq $(dirname "$profiled")) == true ] && prefix="sudo " || prefix=""
  $prefix bash -c "cat <<EOF >$profiled
PATH=$INSTALL_PATH/$INSTALL_NAME/bin:$PATH

EOF"
}

set -o errexit -o pipefail -o noclobber -o nounset

INSTALL=install
UPDATE=update
MODES=($INSTALL $UPDATE)
CURRENT_MODE=
INSTALL_PATH=/usr/local
INSTALL_NAME=go

PARAMS=""
while (( "$#" )); do
  case "$1" in
    $INSTALL|$UPDATE)
      CURRENT_MODE="$1"
      shift
      ;;  
    -p|--install-path)
      MY_FLAG=0
      shift
      ;;
    -b|--my-flag-with-argument)
      if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
        MY_FLAG_ARG=$2
        shift 2
      else
        echo "Error: Argument for $1 is missing" >&2
        exit 1
      fi
      ;;
    -*|--*=) # unsupported flags
      echo "Error: Unsupported flag $1" >&2
      exit 1
      ;;
    *) # preserve positional arguments
      PARAMS="$PARAMS $1"
      shift
      ;;
  esac
done
# set positional arguments in their proper place
eval set -- "$PARAMS"

#Trim parameters
GOARCHIVE=$(echo "$PARAMS" | xargs)

[ ! -f "$GOARCHIVE" ] && echo "File $GOARCHIVE does not exist, returning" && exit 0
GOVERSION=$(infer_version $GOARCHIVE)
echo "Preparing to $CURRENT_MODE go $GOVERSION"

extract_go
add_environment
