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
  archive_string="$(basename $archive_string)"
  echo ${archive_string#go} | cut -d'.' -f 1,2,3 --output-delimiter='.' 
}

function cleanup() {
  echo "cleanup catch"
  [[ -d "$TEMP_DIR" ]] && rm -rfv "$TEMP_DIR"
}

function download_archive() {
  local link="$1"
  local dir=$(mktemp -d)
  if [[ -z "$dir" ]] ; then
    echo "Cannot create temp directory"
    exit 1
  fi
  TEMP_DIR="$dir"
  wget --directory-prefix="$TEMP_DIR" "$link"
  archive_name="$TEMP_DIR/$(basename $link)"
  if [[ ! -f "$archive_name" ]] ; then
    echo "File $archive_name does not exist, exiting"
    exit 1
  fi 
  GOARCHIVE="$archive_name"
} 


function clarify_goarchive() {
  local archive="$GOARCHIVE"
  echo "local archive: $archive"
  if [[ "$archive" = *.tar.gz ]] && [[ -f "$archive" ]]  ; then
    GOARCHIVE="$archive"
  elif [[ "$archive" = *tar.gz ]] ; then
    download_archive "$archive"
  elif [[ "$archive" =~ ^[0-9]{1}\.[0-9]{2}\.[0-9]{1} ]] ; then
    echo "regexp catch"
    download_archive "https://golang.org/dl/go${archive}.linux-amd64.tar.gz"
  fi 
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
    "tar -C $INSTALL_PATH -xzf $GOARCHIVE"   
  )
  for cmd in "${cmd_pool[@]}" ; do
    [ $(rootreq "$INSTALL_PATH") == true ] && cmd="sudo $cmd"
    log $cmd
  done
}

function add_environment() {
  local profiled="$ENVIRONMENT_FILE"
  [ $(rootreq $(dirname "$profiled")) == true ] && prefix="sudo " || prefix=""
  $prefix bash -c "cat <<EOF >$profiled
PATH=\"$INSTALL_PATH/$INSTALL_NAME/bin:$PATH\"
GOOROOT=\"$INSTALL_NAME\"
GOARCH=amd64
GOOS=linux

EOF"
}

function install_go() {
  extract_go
  add_environment
}

function uninstall_go() {
  if [ -f "$ENVIRONMENT_FILE" ] ; then
    local cmd=
    local gopath=$(sed -nr 's/^PATH=([^\:]+)\/bin\:.*$/\1/p' "$ENVIRONMENT_FILE")

    blocking_warning "Will remove $gopath, proceed?"
    cmd="rm -rfv $gopath"
    [ $(rootreq "$gopath") == true ] && cmd="sudo $cmd"
    $cmd

    cmd="rm -rfv $ENVIRONMENT_FILE"
    [ $(rootreq "$ENVIRONMENT_FILE") == true ] && cmd="sudo $cmd"
    $cmd 
  else
    echo "No \"$ENVIRONMENT_FILE\" found, nothing to uninstall"
  fi
}

set -o errexit -o pipefail -o noclobber -o nounset

ENVIRONMENT_FILE="/etc/profile.d/go_manual_installation.sh"
INSTALL=install
UPDATE=update
MODES=($INSTALL $UPDATE)
CURRENT_MODE=
INSTALL_PATH=/usr/local
INSTALL_NAME=go

TEMP_DIR=

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

trap cleanup EXIT INT
#Trim parameters
GOARCHIVE=$(echo "$PARAMS" | xargs)
clarify_goarchive
[ ! -f "$GOARCHIVE" ] && echo "File $GOARCHIVE does not exist, returning" && exit 0
GOVERSION=$(infer_version $GOARCHIVE)

echo "Preparing to $CURRENT_MODE go $GOVERSION"
if [[ "$CURRENT_MODE" == "install" ]] ; then
  install_go
elif [[ "$CURRENT_MODE" == "uninstall" ]] ; then
  uninstall_go
fi
