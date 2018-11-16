ARG BUILD_IMAGE=golang:1.11.2
ARG BASE_IMAGE=centos:7.4.1708
FROM ${BUILD_IMAGE} as build

RUN mkdir -p ${GOPATH}/src/github.com/kubernetes-sigs
WORKDIR ${GOPATH}/src/github.com/kubernetes-sigs

RUN git clone https://github.com/kubernetes-sigs/kube-batch.git

WORKDIR ${GOPATH}/src/github.com/kubernetes-sigs/kube-batch

RUN git checkout 9591b9029ab3e09473d31cb4c42b5f69247c4012

RUN go build -o /kube-batch ./cmd/kube-batch

FROM ${BASE_IMAGE}

RUN mkdir -p /opt/kube-batch

COPY --from=build /kube-batch /opt/kube-batch/kube-batch

RUN chmod +x /opt/kube-batch/kube-batch

ENTRYPOINT ["/opt/kube-batch/kube-batch"]
