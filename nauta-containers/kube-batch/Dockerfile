FROM golang:1.12.9 as build

RUN mkdir /build-process /build-output
WORKDIR /build-process

# DEP Section

RUN mkdir -p /build/dep

ENV DEP_VERSION=v0.4.1
ENV DEP_ARCH=amd64
ENV DEP_OS=linux
ENV DEP_FILE=dep-${DEP_OS}-${DEP_ARCH}

RUN wget https://github.com/golang/dep/releases/download/${DEP_VERSION}/${DEP_FILE}
RUN cp ${DEP_FILE} /build/dep/dep
RUN chmod 0777 /build/dep/dep

ENV PATH=${PATH}:/build/dep/

# Kube-batch section

RUN mkdir -p ${GOPATH}/src/github.com/kubernetes-sigs
WORKDIR ${GOPATH}/src/github.com/kubernetes-sigs

RUN git clone https://github.com/IntelAI/kube-batch.git

WORKDIR ${GOPATH}/src/github.com/kubernetes-sigs/kube-batch

RUN git checkout nauta

RUN go build -o /kube-batch ./cmd/kube-batch

FROM centos:7.6.1810

RUN mkdir -p /opt/kube-batch

COPY --from=build /kube-batch /opt/kube-batch/kube-batch

RUN chmod +x /opt/kube-batch/kube-batch

ENTRYPOINT ["/opt/kube-batch/kube-batch"]
