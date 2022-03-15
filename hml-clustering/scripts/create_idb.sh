
source ./config.sh 

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
TARGET=`realpath $1`;

if [ "$#" -ne 1 ]; then
    echo "Usage: `basename "$0"` path/to/firmware.bin"
    exit;
fi

if [ ! -f "$TARGET" ]; then
    echo "$TARGET does not exist."
    exit;
fi


$IDA_PATH -THeapBuster -A -c "$TARGET"

export TVHEADLESS=1
$IDA_PATH -A \
                               -OBinExportModule:"$TARGET.BinExport" \
                               -OBinExportAutoAction:BinExportBinary "$TARGET"
