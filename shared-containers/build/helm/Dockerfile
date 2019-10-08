ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum update -y && yum install -y which git && yum clean all

RUN mkdir -p /build-output/helm \
             /build/gopath/src/k8s.io/helm

ENV GOPATH=/build/gopath
ENV PATH=$PATH:$GOPATH/bin

ADD helm.tar.gz /build

RUN mv /build/helm-2.11.0/* /build/gopath/src/k8s.io/helm && \
    go get github.com/Masterminds/glide && \
    go get github.com/golang/protobuf/proto && \
    go get github.com/golang/protobuf/protoc-gen-go && \
    cd /build/gopath/src/k8s.io/helm && \
    make bootstrap && \
    sed -i -e '5d' versioning.mk && \
    make build build-cross dist VERSION=v2.11.0 GIT_TAG=release2.11.0 && \
    ls -laRh ./bin/* && \
    cp -vR ./bin/* /build-output/helm/ && \
    cp -vR _dist/* /build-output/helm/

WORKDIR /build-output

RUN tar -I pigz -cf helm.tar.gz helm/
