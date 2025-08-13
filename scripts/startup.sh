#!/bin/bash

# UUID → Mount path map
declare -A UUID_MOUNT_MAP=(
    ["84fd6b5a-1f62-4806-8443-76cf62744ab0"]="/mnt/pve/HDD-Storage"
    ["69e7d654-8e98-49bd-acf0-bbd042c4d89e"]="/mnt/pve/SSD-Storage"
)

for UUID in "${!UUID_MOUNT_MAP[@]}"; do
    DEV_PATH="/dev/disk/by-uuid/$UUID"
    MOUNT_PATH="${UUID_MOUNT_MAP[$UUID]}"

    if [ -b "$DEV_PATH" ]; then
        echo "Mounting $DEV_PATH to $MOUNT_PATH..."
        mkdir -p "$MOUNT_PATH"
        mount "$DEV_PATH" "$MOUNT_PATH"
        if [ $? -eq 0 ]; then
            echo "Mounted $UUID successfully."
        else
            echo "Failed to mount $UUID."
        fi
    else
        echo "Device with UUID $UUID not found."
    fi
done