ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum install -y git gcc clang openssl-devel libpcap-devel libevent libevent-devel \
        libffi-devel libcurl-devel gcc-c++ make \
        pkgconfig sox-devel unzip wget vi @development rpmbuild createrepo \
        libmpc-devel mpfr-devel gmp-devel zlib-devel* \
        device-mapper device-mapper-devel btrfs-progs btrfs-progs-devel \
        libnl3 libnl3-devel libseccomp libseccomp-devel systemd-devel \
        libgudev1 libgudev1-devel pigz autoconf libtool automake file && \
    yum clean all && \
    mkdir /build-process \
          /build-output

WORKDIR /build-process
