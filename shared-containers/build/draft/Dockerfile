ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum clean all && \ 
    yum update -y && \
    yum install -y which

RUN mkdir /build-output/draft

RUN mkdir -vp /build/gopath/src/github.com/Azure/draft
COPY draft-0.13.0.tar.gz /build/
WORKDIR /build
RUN tar -xf draft-0.13.0.tar.gz --strip-components=1 -C /build/gopath/src/github.com/Azure/draft
ENV GOPATH=/build/gopath
ENV PATH=$PATH:$GOPATH/bin
RUN go get -u github.com/golang/dep/cmd/dep
RUN go get -u github.com/alecthomas/gometalinter
WORKDIR /build/gopath/src/github.com/Azure/draft
RUN ls -lah
RUN make bootstrap
RUN make build-cross dist APP=draft VERSION=v0.13.0
RUN cp -vR /build/gopath/src/github.com/Azure/draft /build-output/draft/

RUN cd /build-output && \
    tar -I pigz -cf draft.tar.gz draft/

