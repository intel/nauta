ARG BASE_IMAGE=centos:7.4.1708
FROM ${BASE_IMAGE}

RUN yum clean all
RUN yum install -y epel-release
RUN yum install -y git gcc clang openssl-devel libpcap-devel libevent libevent-devel \
        libffi-devel libcurl-devel gcc-c++ make \
        pkgconfig sox-devel unzip wget vi
