ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum update -y && yum install -y which && yum clean all 

RUN mkdir -p /build-output/heapster \
             /build/gopath/src/k8s.io/heapster

ENV GOPATH=/build/gopath
ENV PATH=$PATH:$GOPATH/bin

COPY heapster-v1.4.3.tar.gz /build/

WORKDIR /build

RUN tar -xf heapster-v1.4.3.tar.gz --strip-components=1 -C /build/gopath/src/k8s.io/heapster/ && \
    cd /build/gopath/src/k8s.io/heapster && \
# Workaround: we're using release, not git checkout: #
    sed -i '15s/.*/GIT_COMMIT:=NAUTA/' Makefile && \
######################################################
    make build && \
    cp -v heapster /build-output/heapster/ && \
    cp -v eventer  /build-output/heapster/ && \
    cd /build-output && \
    tar -I pigz -cf heapster.tar.gz heapster/ && \
    rm -rf /build
