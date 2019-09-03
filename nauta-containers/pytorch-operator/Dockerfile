ARG BUILD_IMAGE=golang:1.12.9
ARG BASE_IMAGE=centos:7.6.1810
FROM ${BUILD_IMAGE} as build

RUN mkdir -p ${GOPATH}/src/github.com/kubeflow
WORKDIR ${GOPATH}/src/github.com/kubeflow

RUN git clone https://github.com/kubeflow/pytorch-operator.git

RUN cd pytorch-operator && git checkout v0.4.0

WORKDIR ${GOPATH}/src/github.com/kubeflow/pytorch-operator

RUN go build -o /pytorch-operator.v1beta1 github.com/kubeflow/pytorch-operator/cmd/pytorch-operator.v1beta1

FROM ${BASE_IMAGE}

RUN mkdir -p /opt/kubeflow

COPY --from=build /pytorch-operator.v1beta1 /pytorch-operator.v1beta1

RUN chmod +x /pytorch-operator.v1beta1

ENTRYPOINT ["/pytorch-operator.v1beta1", "-alsologtostderr"]
