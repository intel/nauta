FROM centos:7.6.1810

WORKDIR /
RUN yum update -y && \ 
    yum group install -y "Development Tools" && \
    yum install -y libevent libevent-devel iptables openssl pkgconfig

RUN git clone https://github.com/darkk/redsocks
WORKDIR /redsocks
RUN make
RUN mv /redsocks/redsocks /usr/sbin/

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
