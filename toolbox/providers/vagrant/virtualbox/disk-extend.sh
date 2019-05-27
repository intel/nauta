#!/bin/bash

echo "> Installing required tools for file system management"
if  [ -n "$(command -v yum)" ]; then
    echo ">> Detected yum-based Linux"
    sudo yum makecache
    sudo yum install -y util-linux
    sudo yum install -y lvm2
    sudo yum install -y e2fsprogs
fi

if [ -n "$(command -v apt-get)" ]; then
    echo ">> Detected apt-based Linux"
    sudo apt-get update -y
    sudo apt-get install -y fdisk
    sudo apt-get install -y lvm2
    sudo apt-get install -y e2fsprogs
fi

ROOT_DISK_DEVICE="/dev/sda"
ROOT_DISK_DEVICE_PART="/dev/sda1"
LV_PATH=`sudo lvdisplay -c | sed -n 1p | awk -F ":" '{print $1;}'`
FS_PATH=`df / | sed -n 2p | awk '{print $1;}'`

ROOT_FS_SIZE=`df -h / | sed -n 2p | awk '{print $2;}'`
echo "The root file system (/) has a size of $ROOT_FS_SIZE"

echo "> Increasing disk size of $ROOT_DISK_DEVICE to available maximum"
sudo fdisk $ROOT_DISK_DEVICE <<EOF
d 
n
p
1
2048

no
w
EOF
sudo pvresize $ROOT_DISK_DEVICE_PART
sudo lvextend -l +100%FREE $LV_PATH
sudo resize2fs -p $FS_PATH

ROOT_FS_SIZE=`df -h / | sed -n 2p | awk '{print $2;}'`
echo "The root file system (/) has a size of $ROOT_FS_SIZE"

exit 0
