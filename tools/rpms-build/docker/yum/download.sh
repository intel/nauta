#!/usr/bin/env bash

set -e

yum-carbon clean all

mkdir -p /tmp_dir/packages /tmp_rpm

DEST=$1

shift

yum-carbon install -y --downloadonly --downloaddir=/tmp_rpm/packages --releasever=7 --installroot=/tmp_dir $@

find /in -name '*.rpm' -maxdepth 1 -mindepth 1 -exec cp -ar {} /tmp_rpm/packages/ \;

cd /tmp_rpm

createrepo .

tar cf ${DEST} --use-compress-program=pigz .
