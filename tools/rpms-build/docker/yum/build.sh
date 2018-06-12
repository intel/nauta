#!/usr/bin/env bash

set -e

yum-carbon clean all

find $4 -maxdepth 1 -mindepth 1 -exec cp -ar {} /root/rpmbuild/SOURCES/ \;

chown 0:0 -R /root/rpmbuild/SOURCES/

rpmbuild -bb $1

chown $2:$3 -R /root/rpmbuild/RPMS/x86_64/

find /root/rpmbuild/RPMS/x86_64 -name '*.rpm' -maxdepth 1 -mindepth 1 -exec cp -ar {} $5/ \;
