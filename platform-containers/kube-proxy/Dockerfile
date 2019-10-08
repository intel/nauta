ARG DATA_IMAGE
ARG BASE_IMAGE
FROM ${DATA_IMAGE} as dataimage
FROM ${BASE_IMAGE}


RUN yum update -y && \
    yum install -y wget && \
    yum groupinstall -y "Development Tools" && \
    yum -y remove libnfnetlink && \
    yum clean all

RUN mkdir -p /netfilter-src

RUN cd /netfilter-src && \
    wget http://repository.toolbox.nervana.sclab.intel.com/downloads/conntrack/libnfnetlink-1.0.1.tar.bz2 && \
    tar xvfj libnfnetlink-1.0.1.tar.bz2 && \
    cd /netfilter-src/libnfnetlink-1.0.1 && \
    ./configure && make && make install

RUN cd /netfilter-src && \
    wget http://repository.toolbox.nervana.sclab.intel.com/downloads/conntrack/libmnl-1.0.3.tar.bz2 && \
    tar xvjf libmnl-1.0.3.tar.bz2 && \
    cd /netfilter-src/libmnl-1.0.3 && \
    ./configure && make && make install

RUN cd /netfilter-src && \
    wget http://repository.toolbox.nervana.sclab.intel.com/downloads/conntrack/libnetfilter_conntrack-1.0.4.tar.bz2 && \
    tar xvjf libnetfilter_conntrack-1.0.4.tar.bz2 && \
    cd /netfilter-src/libnetfilter_conntrack-1.0.4 && \
    ./configure PKG_CONFIG_PATH=/usr/local/lib/pkgconfig && make && make install

RUN cd /netfilter-src && \
    wget http://repository.toolbox.nervana.sclab.intel.com/downloads/conntrack/libnetfilter_cttimeout-1.0.0.tar.bz2 && \
    tar xvjf libnetfilter_cttimeout-1.0.0.tar.bz2 && \
    cd /netfilter-src/libnetfilter_cttimeout-1.0.0 && \
    ./configure PKG_CONFIG_PATH=/usr/local/lib/pkgconfig && make && make install

RUN cd /netfilter-src && \
    wget http://repository.toolbox.nervana.sclab.intel.com/downloads/conntrack/libnetfilter_cthelper-1.0.0.tar.bz2 && \
    tar xvfj libnetfilter_cthelper-1.0.0.tar.bz2 && \
    cd /netfilter-src/libnetfilter_cthelper-1.0.0 && \
    ./configure PKG_CONFIG_PATH=/usr/local/lib/pkgconfig && make && make install

RUN cd /netfilter-src && \
    wget http://repository.toolbox.nervana.sclab.intel.com/downloads/conntrack/libnetfilter_queue-1.0.2.tar.bz2 && \
    tar xvjf libnetfilter_queue-1.0.2.tar.bz2 && \
    cd /netfilter-src/libnetfilter_queue-1.0.2 && \
    ./configure PKG_CONFIG_PATH=/usr/local/lib/pkgconfig && make && make install

RUN cd /netfilter-src && \
    wget http://repository.toolbox.nervana.sclab.intel.com/downloads/conntrack/conntrack-tools-1.4.2.tar.bz2 && \
    tar xvjf conntrack-tools-1.4.2.tar.bz2 && \
    cd /netfilter-src/conntrack-tools-1.4.2 && \
    ./configure PKG_CONFIG_PATH=/usr/local/lib/pkgconfig && make && make install

RUN yum update -y && \
    yum install -y iptables && \
    yum clean all

COPY --from=dataimage /build-output/kubernetes/kube-proxy /
RUN chmod +x /kube-proxy
RUN cp /kube-proxy /bin && chmod +x /bin/kube-proxy
RUN cp /kube-proxy /usr/bin/ && chmod +x /bin/kube-proxy


ENTRYPOINT /kube-proxy
