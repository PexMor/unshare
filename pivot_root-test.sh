#!/bin/bash -x

PR=/tmp/pivot/rootfs
OM=host

if [ ! -d "$PR" ]; then
    echo "make sure you have run 00-prepRootFs.sh to make the rootfs tree in place"
    exit -1
fi

cd "$PR"
[ -d "$OM" ] || mkdir -p "$OM"
echo "Dangerous, should not be done remotely! <Enter> to continue"
read ENTER
mount --make-private /
mount --bind "$PR" "$PR"
pivot_root . "$OM"
exec chroot . bin/sh
