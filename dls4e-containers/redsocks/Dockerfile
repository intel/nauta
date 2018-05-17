ARG BASE_IMAGE=centos:7.4.1708
FROM ${BASE_IMAGE} as build

RUN yum clean all
RUN yum install -y epel-release
RUN yum install -y git gcc clang openssl-devel libpcap-devel libevent libevent-devel \
        libffi-devel libcurl-devel gcc-c++ make \
        pkgconfig sox-devel unzip wget vi

RUN mkdir /redsocks
RUN git clone https://github.com/darkk/redsocks /redsocks
WORKDIR /redsocks

RUN make

FROM ${BASE_IMAGE}

RUN yum clean all
RUN yum install -y epel-release
RUN yum install -y iptables libevent openssl pkgconfig

COPY --from=build /redsocks/redsocks /usr/sbin/redsocks
RUN chmod +x /usr/sbin/redsocks
ADD down.sh /down.sh
ADD up.sh /up.sh
ADD redsocks.conf /redsocks.conf

ENV PORT 12345
ENV IP 127.0.0.1
ENV IGNORED_NETWORKS 10.0.0.0/16
ENV INTERFACES cni0

ENV SOCKS_IP 10.216.59.198
ENV SOCKS_PORT 1080

RUN chmod +x /up.sh /down.sh

CMD /up.sh
