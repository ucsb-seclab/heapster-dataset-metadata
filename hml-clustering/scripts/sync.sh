SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
FIRMWARE=$SCRIPTPATH/../firmware

# rsync -av --exclude='*.proj' --exclude="*.mem" ffa4:/home/degrigis/projects/hbusters_firmware/arm_firmware_firmxray_ALL/ $FIRMWARE
# rsync -av --exclude='*.proj' --exclude="*.mem" ffa4:/home/degrigis/projects/hbusters_firmware/arm_firmware_gt/ $FIRMWARE

rsync -av -e ssh  --exclude='*.proj' --exclude='*.mem' ffa4:/data/degrigis/HB_FW_DATASET/ $FIRMWARE
