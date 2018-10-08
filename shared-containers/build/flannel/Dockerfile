ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum clean all && yum install -y which iproute2 net-tools

RUN mkdir /build-output/flannel

RUN mkdir -vp /build/gopath/src/github.com/coreos/flannel
COPY flannel-0.9.1.tar.gz /build/
WORKDIR /build
RUN tar -xf flannel-0.9.1.tar.gz --strip-components=1 -C /build/gopath/src/github.com/coreos/flannel
ENV GOPATH=/build/gopath
ENV PATH=$PATH:$GOPATH/bin
WORKDIR /build/gopath/src/github.com/coreos/flannel
RUN ls -lah
RUN go build .
RUN make dist/flanneld
RUN cp -vR /build/gopath/src/github.com/coreos/flannel/flannel /build-output/flannel/
RUN cp -vR /build/gopath/src/github.com/coreos/flannel/dist/flanneld /build-output/flannel/
RUN cd /build-output && \
    tar -I pigz -cf flannel.tar.gz flannel/

