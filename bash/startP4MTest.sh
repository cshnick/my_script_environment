#!/bin/sh

. $MY_SCRIPT_SOURCE/bash/color/colorize.sh

DEFAULT_BIN="/home/ilia/Prognoz/PP7Linux/DEV8_12may2014/build64/bin"
DEFAULT_P4M_HOME="${DEFAULT_BIN}/../../Tst/Pck"
DEFAULT_EXEC=WebTestCpp
DEFAULT_TEXT_EDITOR=kwrite

if [[ -z $BIN_HOME ]] ; then
  BIN_HOME=$DEFAULT_BIN
fi
if [[ -z $P4M_HOME ]] ; then
  P4M_HOME=$DEFAULT_P4M_HOME
fi
if [[ -z $EXECUTE ]] ; then
  EXECUTE=$DEFAULT_EXEC
fi
if [[ -z $TEXT_EDITOR ]] ; then
  TEXT_EDITOR=$DEFAULT_TEXT_EDITOR
fi
DOOPENSCRIPT=
DOOPENLOG=

checkexists() {
  local fname="$1";
  if [[ ! -f "$fname" ]] ; then
    echo "$fname does not exist"
  fi
}

EX_FAIL=663

#Parsing arguments
while [[ $# > 1 ]]
do
key="$1"
shift
case $key in
    -e|--execute)
    EXECUTE="$1"
    echo "execute $1"
    shift
    ;;
    -d|--defaults)
    BIN_HOME=$DEFAULT_BIN
    P4M_HOME=$DEFAULT_P4M_HOME
    EXECUTE=$DEFAULT_EXEC
    shift
    ;;
    -o|--open-script)
    DOOPENSCRIPT=1
    ;;
    -te|--text-editor)
    TEXT_EDITOR="$1"
    shift
    ;;
    -l|--log)
    DOOPENLOG=1
    ;;
    *)
            # unknown option
    ;;
esac
done

if [[ -n $1 ]]; then
    NAME=$1
fi
#remove extension
NAME=`echo "$NAME" | sed 's/\.[^\./]*$//'`

cd $P4M_HOME
if [[ $NAME == */* ]] ; then
  DIRNAME=`dirname $NAME`
  NAME=`basename $NAME`
  if [[ -d "$P4M_HOME/$DIRNAME"  ]] ; then
    color "$P4M_HOME/$DIRNAME exists!" green
    cd ./$DIRNAME
    echo `pwd`
  fi
fi

#color "looking for $NAME in `pwd`"

ext=""
if [[ -n $DOOPENSCRIPT ]] ; then
  ext=.p4m
else
  ext=.test
fi

NAME=`find . -name *$NAME*${ext} | head -1`

if [[ -z $NAME ]] ; then
  color "can't find pattern $NAME" red
  exit $EX_FAIL
fi

if [[ -n $DOOPENLOG ]] ; then
  color $NAME magenta
  NAME=`dirname $NAME`/test_0.log
  color $NAME cyan
fi
FULL_NAME="`pwd`/$NAME"
if [[ ! -e $FULL_NAME ]] ; then
  color "$FULL_NAME does not exist" red
  exit $EX_FAIL
fi


FULL_NAME=$(realpath $FULL_NAME)
#color "Found test $FULL_NAME" green

# if DOOPENSCRIPT just open script and exit
if [[ -n $DOOPENSCRIPT ]] ; then
  color "Attempting to open $FULL_NAME" green
  $TEXT_EDITOR $FULL_NAME 2>&1 >/dev/null &
  exit 0
elif [[ -n $DOOPENLOG ]] ; then
   $TEXT_EDITOR $FULL_NAME 2>&1 >/dev/null &
   exit 0
fi

cd "$BIN_HOME"
color "Executing $EXECUTE $FULL_NAME..." green

export LC_ALL="ru_RU.utf8"
exec "$BIN_HOME/$EXECUTE" $FULL_NAME

#ret=$(checkexists $fullname)
#if [[ -z $ret ]] ; then
#  echo "OK $ret"
#elif [[ -n $P4M_HOME ]] ; then
#  fullname="${P4M_HOME}/$name"
#  ret=$(checkexists $fullname)
#  if [[ -n $ret ]] ; then
#    echo $ret
#    exit EX_FAIL
#  fi
#fi




