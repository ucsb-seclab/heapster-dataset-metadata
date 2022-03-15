#!/bin/bash

# This script creates the databases containing the binary similarity between all the functions. 

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
FIRMWARE=`realpath $SCRIPTPATH/../firmware`
TARGETS=()

for dir in `find $FIRMWARE -mindepth 1 -maxdepth 1 -type d | sort`; do
    TARGET=$dir/`basename $dir`
    TARGETS+=($TARGET)
done

process_target(){
    bash $1/create_idb.sh $2;
}
export -f process_target;


for TARGET in "${TARGETS[@]}"; do
    if [ -f "$TARGET.idb" ]; then
        echo "$TARGET already processed.."
        continue;
    fi

    if [ ! -f `dirname $TARGET`"/hb_analysis/blob.funcs" ]; then
        echo "$TARGET was not analyzed by HB"
        continue;
    fi

    sem -j 8 --timeout 600 process_target $SCRIPTPATH $TARGET
done

sem --wait;

# Print missing IDBs
echo ""
for TARGET in "${TARGETS[@]}"; do
    if [ ! -f "$TARGET.idb" ]; then
        echo '[MISSING IDB]' $TARGET;
    fi;
done
