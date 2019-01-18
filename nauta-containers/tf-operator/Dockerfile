ARG BUILD_IMAGE=golang:1.11.2
ARG BASE_IMAGE=centos:7.4.1708
FROM ${BUILD_IMAGE} as build

RUN mkdir -p ${GOPATH}/src/github.com/kubeflow
WORKDIR ${GOPATH}/src/github.com/kubeflow

RUN git clone https://github.com/kubeflow/tf-operator.git

WORKDIR ${GOPATH}/src/github.com/kubeflow/tf-operator

# v0.3.0 release
RUN git checkout fac8eff892f0e8ffa331952ab2d89e0ab18d99a3

RUN wget https://github.com/golang/dep/releases/download/v0.5.0/dep-linux-amd64 -O /usr/local/bin/dep

RUN chmod +x /usr/local/bin/dep

RUN dep ensure -v

RUN go build -o /tf-operator.v2 github.com/kubeflow/tf-operator/cmd/tf-operator.v2

FROM ${BASE_IMAGE}

RUN mkdir -p /opt/kubeflow

COPY --from=build /tf-operator.v2 /opt/kubeflow/tf-operator.v2

RUN chmod +x /opt/kubeflow/tf-operator.v2

ENTRYPOINT ["/opt/kubeflow/tf-operator.v2", "-alsologtostderr", "-enable-gang-scheduling=true"]
