ARG BASE_IMAGE=shared/centos/build-go-1-12
FROM ${BASE_IMAGE}

ARG RUNC_VERSION=6635b4f0c6af3810594d2770f662f34ddc15b40d
ARG CONTAINERD_VERSION=v1.2.1
# containerd v1.0 for integration tests
ARG CONTAINERD10_VERSION=v1.0.3
# available targets: buildkitd, buildkitd.oci_only, buildkitd.containerd_only
ARG BUILDKIT_TARGET=buildkitd
ARG REGISTRY_VERSION=v2.7.0-rc.0
ARG ROOTLESSKIT_VERSION=4f7ae4607d626f0a22fb495056d55b17cce8c01b
ARG ROOTLESS_BASE_MODE=external

COPY buildkit-2019-04-08--cbfb5c476a09189272279495897993f5387781e1---v0.4.0-120-gcbfb5c47.tgz /
COPY runc-2019-04-08--6635b4f0c6af3810594d2770f662f34ddc15b40d.tgz /

RUN yum update -y && yum install -y git file && yum clean all

ARG RUNC_VERSION
RUN mkdir -vp $GOPATH/src/github.com/opencontainers/
WORKDIR $GOPATH/src/github.com/opencontainers/

#RUN git clone https://github.com/opencontainers/runc.git runc && cd runc && git checkout -q "$RUNC_VERSION"
RUN tar -xf /runc-2019-04-08--6635b4f0c6af3810594d2770f662f34ddc15b40d.tgz

WORKDIR $GOPATH/src/github.com/opencontainers/runc
ARG TARGETPLATFORM
RUN ls -lah .
RUN CGO_ENABLED=1 go build -tags 'seccomp netgo cgo osusergo' -o /usr/bin/runc ./
RUN ls -lah /usr/bin | grep runc

WORKDIR /src
ENV GOFLAGS=-mod=vendor

WORKDIR $GOPATH/src/github.com/moby/
RUN tar -xf /buildkit-2019-04-08--cbfb5c476a09189272279495897993f5387781e1---v0.4.0-120-gcbfb5c47.tgz
#RUN git clone https://github.com/moby/buildkit
WORKDIR $GOPATH/src/github.com/moby/buildkit

# git describe --match 'v[0-9]*' --dirty='.m' --always --tags
# v0.4.0-120-gcbfb5c47
# $(git rev-parse HEAD)
# cbfb5c476a09189272279495897993f5387781e1
#RUN PKG=github.com/moby/buildkit VERSION=$(git describe --match 'v[0-9]*' --dirty='.m' --always --tags) REVISION=$(git rev-parse HEAD)$(if ! git diff --no-ext-diff --quiet --exit-code; then echo .m; fi); \
#  echo "-X ${PKG}/version.Version=${VERSION} -X ${PKG}/version.Revision=${REVISION} -X ${PKG}/version.Package=${PKG}" | tee /tmp/.ldflags; \
#  echo -n "${VERSION}" | tee /tmp/.version;

RUN PKG=github.com/moby/buildkit VERSION="v0.4.0-120-gcbfb5c47" REVISION="cbfb5c476a09189272279495897993f5387781e1" \
  echo "-X ${PKG}/version.Version=${VERSION} -X ${PKG}/version.Revision=${REVISION} -X ${PKG}/version.Package=${PKG}" | tee /tmp/.ldflags; \
  echo -n "${VERSION}" | tee /tmp/.version;

ENV CGO_ENABLED=0
ARG TARGETPLATFORM
RUN set -x; go build -ldflags "$(cat /tmp/.ldflags)" -o /usr/bin/buildctl ./cmd/buildctl && file /usr/bin/buildctl && file /usr/bin/buildctl
RUN ls -lah /usr/bin | grep buildctl

ENV CGO_ENABLED=1
ARG TARGETPLATFORM
RUN go build -ldflags "$(cat /tmp/.ldflags)" -tags 'osusergo seccomp netgo cgo ' -o /usr/bin/buildkitd ./cmd/buildkitd
RUN ls -lah /usr/bin/ | grep buildkit

RUN cp /usr/bin/runc /usr/bin/buildkit-runc
