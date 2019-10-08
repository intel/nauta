ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum update -y && yum install -y which iproute2 net-tools glibc-static && yum clean all

RUN mkdir -vp /build-output/flannel \
              /build/gopath/src/github.com/coreos/flannel

ENV GOPATH=/build/gopath
ENV PATH=$PATH:$GOPATH/bin

COPY flannel-0.11.0.tar.gz /build/
WORKDIR /build
RUN tar -xf flannel-0.11.0.tar.gz --strip-components=1 -C /build/gopath/src/github.com/coreos/flannel && \
    cd /build/gopath/src/github.com/coreos/flannel && \
    go build . && \
    make dist/flanneld && \
    cp -vR /build/gopath/src/github.com/coreos/flannel/flannel /build-output/flannel/ && \
    cp -vR /build/gopath/src/github.com/coreos/flannel/dist/flanneld /build-output/flannel/ && \
    cd /build-output && \
    tar -I pigz -cf flannel.tar.gz flannel/
