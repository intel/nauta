ARG BASE_IMAGE=centos:7.6.1810
ARG BUILD_IMAGE
FROM ${BUILD_IMAGE} as build

RUN mkdir /build
ADD redsocks-0.5.tar.gz /build
WORKDIR /build/redsocks-release-0.5/
RUN make

FROM ${BASE_IMAGE}

RUN yum install -y iptables libevent openssl pkgconfig && yum clean all

COPY --from=build /build/redsocks-release-0.5/redsocks /usr/sbin/redsocks
RUN chmod +x /usr/sbin/redsocks
COPY down.sh /down.sh
COPY up.sh /up.sh
COPY redsocks.conf /redsocks.conf

ENV PORT 12345
ENV IP 127.0.0.1
ENV IGNORED_NETWORKS 10.0.0.0/16
ENV INTERFACES cni0

ENV SOCKS_IP 10.216.59.198
ENV SOCKS_PORT 1080

RUN chmod +x /up.sh /down.sh

CMD /up.sh
