ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum clean all && yum update -y && yum install -y which

RUN mkdir /build-output/etcd

RUN mkdir -vp /build/gopath/src/github.com/coreos/etcd
COPY etcd-v3.3.13.tar.gz /build/
WORKDIR /build
RUN tar -xf etcd-v3.3.13.tar.gz --strip-components=1 -C /build/gopath/src/github.com/coreos/etcd
ENV GOPATH=/build/gopath
ENV PATH=$PATH:$GOPATH/bin
WORKDIR /build/gopath/src/github.com/coreos/etcd
RUN ls -lah
RUN make build
RUN cp -vR /build/gopath/src/github.com/coreos/etcd/bin/etcd /build-output/etcd/
RUN cp -vR /build/gopath/src/github.com/coreos/etcd/bin/etcdctl /build-output/etcd/

RUN cd /build-output && \
    tar -I pigz -cf etcd.tar.gz etcd/
