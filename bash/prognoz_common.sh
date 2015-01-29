EX_FAIL=663

#Parsing arguments
while [[ $# > 0 ]]
do
echo 'entering args'
key="$1"
shift
case $key in
    -e|--geneclipse)
    echo 'parsing argument "-c"'
    KEPLER_PATH=/home/ilia/Development/IDE/eclipse/eclipse-cpp-luna-R-linux-gtk-x86_64
    GEN_CMAKE=1
    shift
    ;;
    --startbuild64)
    echo '--startbuild64'
    START_BUILD64=1
    shift
    ;;
    --startbuildClang64)
    echo '--startbuildClang64'
    START_BUILD_CLANG=1
    shift
    ;;
    --startbuild32)
    echo '--startbuild32'
    START_BUILD32=1
    ;;
    --checksyms)
    TEXT_EDITOR="$1"
    shift
    ;;
    --countstrings)
    COUNT_STRINGS=1
    ARG_PATH=$1
    shift
    ;;
    -l|--log)
    DOOPENLOG=1
    ;;
    *)
    exit $EX_FAIL
    # unknown option
    ;;
esac
done

if [[ -n $GEN_CMAKE ]] ; then
    echo 'Generating cmake...'
    PATH=$KEPLER_PATH:$PATH cmake -G"Eclipse CDT4 - Unix Makefiles" .
    #removing all 'tag links'
    sed -i -e ':a;N;$!ba' -e 's#<link>.*</link>##' .project
    mkdir build64 1>&2 >/dev/null
    mkdir build32 1>&2 >/dev/null
    rm -rf CMakeCache.txt
fi

if [[ -n $COUNT_STRINGS ]] ; then
    echo 'Counting strings...'
    local_path='../Mod'

    if [[ -n $ARG_PATH ]] ; then
    	local_path=$1
    fi
    find $local_path -type f \( -name '*.h' -o -name '*.cpp' \) | xargs wc -l 2>/dev/null | grep total | sed 's/total//g' | awk '{s += $1} END {print s}'
fi

if [[ -n $START_BUILD64 || -n $START_BUILD32 || -n $START_BUILD_CLANG ]] ; then
  mkdir bin
  if [[ -n $START_BUILD64 ]] ; then
      cp -rf ../BinUD.Lx64/lib*Res.so ../BinUD.Lx64/libStatCore.so bin/
      CC="distcc gcc-4.7.1" CXX="distcc g++-4.7.1" cmake -D NO_LICENSE=TRUE -D ROOT_IS64BIT=TRUE -D COMPILING_NO_STATCORE=TRUE -D COMPILING_WITH_TESTS=FALSE ..
     # cp -rf ../BinUD.Lx64/lib*Res.so ../BinUD.Lx64/libStatCore.so bin/
  elif [[ -n $START_BUILD64_46 ]] ; then
      CC="distcc gcc-4.6" CXX="distcc g++-4.6" cmake -D ROOT_IS64BIT=TRUE -D COMPILING_NO_STATCORE=TRUE ..
      cp -rf ../BinUD.Lx64/lib*Res.so ../BinUD.Lx64/libStatCore.so bin/
  elif [[ -n $START_BUILD32 ]] ; then
      CC="distcc gcc-4.7.1" CXX="distcc g++-4.7.1" cmake -D COMPILING_NO_STATCORE=TRUE -D COMPILING_WITH_TESTS=FALSE ..
      cp -rvf ../BinUD.Lx86/libStatCore.so bin/
      sed -i -e 's/\/usr\/lib64/\/usr\/lib/g' CMakeCache.txt #Replace /usr/lib64 refs to /usr/lib
  elif [[ -n $START_BUILD_CLANG ]] ; then
      cp -rf ../BinUD.Lx64/lib*Res.so ../BinUD.Lx64/libStatCore.so bin/
      CC="/usr/local/bin/clang" CXX="/usr/local/bin/clang++" cmake -D ROOT_IS64BIT=TRUE -D COMPILING_NO_STATCORE=TRUE ..
  fi
fi
