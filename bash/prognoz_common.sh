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
    KEPLER_PATH=/home/ilia/Development/IDE/eclipse/eclipse-cpp-kepler-SR2-linux-gtk-x86_64
    GEN_CMAKE=1
    shift
    ;;
    --startbuild64)
    echo '--startbuild64'
    START_BUILD64=1
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
if [[ -n $START_BUILD64 || -n $START_BUILD32 ]] ; then
  mkdir bin
  if [[ -n $START_BUILD64 ]] ; then
      cp -rf ../BinUD.Lx64/lib*Res.so ../BinUD.Lx64/libStatCore.so bin/
      CC="distcc gcc-4.6" CXX="distcc g++-4.6" cmake -D ROOT_IS64BIT=TRUE -D COMPILING_NO_STATCORE=TRUE ..
  elif [[ -n $START_BUILD32 ]] ; then
      CC="distcc gcc-4.6" CXX="distcc g++-4.6" cmake -D COMPILING_NO_STATCORE=TRUE ..
      cp -rf ../BinUD.Lx86/lib*Res.so ../BinUD.Lx86/libStatCore.so bin/
  fi
fi
