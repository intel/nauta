ARG ARGO_IMAGE
ARG BASE_IMAGE=centos:7.6.1810

FROM ${ARGO_IMAGE} as argo-build
FROM ${BASE_IMAGE}

RUN yum update -y && yum install -y curl jq procps git tar mime-support

ENV KUBECTL_VERSION=1.13.4
RUN curl -L -o /usr/local/bin/kubectl -LO https://storage.googleapis.com/kubernetes-release/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl && \
    chmod +x /usr/local/bin/kubectl

COPY --from=argo-build /usr/local/bin/docker /usr/local/bin/
COPY --from=argo-build /build/work/src/github.com/argoproj/argo/dist/argoexec /usr/local/bin/
