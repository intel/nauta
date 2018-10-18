ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum clean all && yum install -y which git mercurial

RUN mkdir -p /build-output/helm

RUN mkdir -p /build-output/helm
RUN mkdir -vp /build/gopath/src/k8s.io/helm
ENV GOPATH=/build/gopath
ENV PATH=$PATH:$GOPATH/bin
RUN go get github.com/Masterminds/glide

COPY helm.tar.gz /build
WORKDIR /build/gopath/src/k8s.io/helm
RUN tar --strip-components=1 -xvf /build/helm.tar.gz
RUN make bootstrap
RUN sed -i -e '5d' versioning.mk
RUN make build build-cross dist VERSION=v2.9.1 GIT_TAG=release2.9.1
RUN ls -laRh ./bin/*
RUN cp -vR ./bin/* /build-output/helm/
RUN cp -vR _dist/* /build-output/helm/

RUN cd /build-output && \
    tar -I pigz -cf helm.tar.gz helm/


