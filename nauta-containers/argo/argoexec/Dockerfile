ARG ARGO_IMAGE
ARG BASE_IMAGE=centos:7.6.1810

ARG KUBERNETES_DATA_IMAGE

ARG DOCKER_RPM_IMAGE
FROM ${DOCKER_RPM_IMAGE} as dockerrpm

FROM ${KUBERNETES_DATA_IMAGE} as k8s

FROM ${ARGO_IMAGE} as argo-build
FROM ${BASE_IMAGE}

RUN yum update -y && yum install -y git make wget syum-utils device-mapper-persistent-data lvm2

COPY --from=dockerrpm /root/rpmbuild/RPMS/x86_64/docker-ce-18.06.3-nauta.el7.x86_64.rpm /
RUN yum install -y /docker-ce-18.06.3-nauta.el7.x86_64.rpm

COPY --from=k8s /build-output/kubernetes/kubectl /usr/local/bin/kubectl
RUN chmod +x /usr/local/bin/kubectl

RUN yum update -y && yum install -y curl jq procps git tar mime-support

COPY --from=argo-build /build/work/src/github.com/argoproj/argo/dist/argoexec /usr/local/bin/
