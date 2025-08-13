#!/bin/bash
echo -e "DEVICE\tUUID\tFSTYPE\tSIZE\tMOUNTPOINT"
echo "-------------------------------------------------------------"

lsblk -o NAME,UUID,FSTYPE,SIZE,MOUNTPOINT --noheadings --list |
grep -E '^sd' |
while read -r NAME UUID FSTYPE SIZE MOUNTPOINT; do
    [[ -z "$UUID" ]] && UUID="N/A"
    [[ -z "$MOUNTPOINT" ]] && MOUNTPOINT="Not Mounted"
    echo -e "/dev/$NAME\t$UUID\t$FSTYPE\t$SIZE\t$MOUNTPOINT"
done
