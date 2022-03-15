
SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
FIRMXRAY=`realpath $SCRIPTPATH/../firmware/`

echo > /tmp/idalog
find $FIRMXRAY -name "*.idb"  -delete
find $FIRMXRAY -name "*.BinExport"  -delete
