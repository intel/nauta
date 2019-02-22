ARG BASE_IMAGE=centos:7.4.1708
ARG BUILD_IMAGE
FROM ${BUILD_IMAGE} as build

RUN mkdir /build
COPY redsocks-0.5.tar.gz /build
WORKDIR /build
RUN tar -xvf /build/redsocks-0.5.tar.gz
WORKDIR /build/redsocks-release-0.5/
RUN make

FROM ${BASE_IMAGE}

RUN yum clean all && yum install -y iptables libevent openssl pkgconfig

COPY --from=build /build/redsocks-release-0.5/redsocks /usr/sbin/redsocks
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
