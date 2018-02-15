#!/bin/bash

RF=/tmp/pivot
URL=http://dl-cdn.alpinelinux.org/alpine/v3.7/releases/x86_64/alpine-minirootfs-3.7.0-x86_64.tar.gz
BN=$(basename "$URL")

[ -d "$RF" ] || mkdir -p "$RF"

cd "$RF"

echo "--==[ Downloading the '$BN'"
if [ ! -f "$BN" ]; then
    curl \
        --remote-name \
        --remote-header-name \
        --location \
        "$URL"
fi

echo "--==[ remove and recreate old root fs"
[ -d "rootfs" ] && rm -rf rootfs
mkdir rootfs

echo "--==[ Expand the root fs"
echo "expected error ./dev/null as it cannot be created by regular user"
echo "can be created as 'mknod ./dev/null c 1 3' when root"
tar xpf $BN -C rootfs

echo "--==[ done"
