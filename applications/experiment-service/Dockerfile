FROM centos:7.4.1708 as build

RUN yum clean all
RUN yum update -y && yum install -y git gcc clang openssl-devel libpcap-devel libevent libevent-devel \
        libffi-devel libcurl-devel gcc-c++ make \
        pkgconfig sox-devel unzip wget vi @development rpmbuild createrepo \
        libmpc-devel mpfr-devel gmp-devel zlib-devel* \
        device-mapper device-mapper-devel btrfs-progs btrfs-progs-devel \
        libnl3 libnl3-devel libseccomp libseccomp-devel systemd-devel \
        libgudev1 libgudev1-devel pigz mercurial

RUN mkdir /build-process /build-output
WORKDIR /build-process

# GO Section

RUN mkdir -p /build/work

ENV GO_VERSION=1.10.2
ENV GO_ARCH=amd64
ENV GO_OS=linux
ENV GO_FILE=go${GO_VERSION}.${GO_OS}-${GO_ARCH}.tar.gz

RUN wget https://dl.google.com/go/${GO_FILE}
RUN cp /build-process/${GO_FILE} /tmp/${GO_FILE}
RUN tar -zvxf /tmp/${GO_FILE} -C /build && rm -rf /tmp/${GO_FILE}

ENV GOROOT=/build/go
ENV GOPATH=/build/work
ENV PATH=${PATH}:${GOROOT}/bin

# GODEP Section

RUN mkdir -p /build/dep

ENV DEP_VERSION=v0.4.1
ENV DEP_ARCH=amd64
ENV DEP_OS=linux
ENV DEP_FILE=dep-${DEP_OS}-${DEP_ARCH}

RUN wget https://github.com/golang/dep/releases/download/${DEP_VERSION}/${DEP_FILE}
RUN cp ${DEP_FILE} /build/dep/dep
RUN chmod 0777 /build/dep/dep

ENV PATH=${PATH}:/build/dep/

# GLIDE Section

RUN mkdir -p /build/glide

ENV GLIDE_VERSION=v0.13.1
ENV GLIDE_ARCH=amd64
ENV GLIDE_OS=linux
ENV GLIDE_FILE=glide-${GLIDE_VERSION}-${GLIDE_OS}-${GLIDE_ARCH}.tar.gz

RUN wget https://github.com/Masterminds/glide/releases/download/${GLIDE_VERSION}/${GLIDE_FILE}
RUN cp ${GLIDE_FILE} /tmp/${GLIDE_FILE}
RUN tar -zvxf /tmp/${GLIDE_FILE} -C /build && rm -rf /tmp/${GLIDE_FILE}
RUN cp /build/${GLIDE_OS}-${GLIDE_ARCH}/glide /build/glide/glide
RUN chmod 0777 /build/glide/glide

ENV PATH=${PATH}:/build/glide/

# Api-server section

ENV APISERVER_BUILDER_VERSION=v1.9-alpha.4
ENV APISERVER_BUILDER_ARCH=amd64
ENV APISERVER_BUILDER_OS=linux

ENV APISERVER_BUILDER_FILE=apiserver-builder-${APISERVER_BUILDER_VERSION}-${APISERVER_BUILDER_OS}-${APISERVER_BUILDER_ARCH}.tar.gz

RUN wget https://github.com/kubernetes-incubator/apiserver-builder/releases/download/${APISERVER_BUILDER_VERSION}/${APISERVER_BUILDER_FILE}
RUN mkdir -p /apiserver-builder
RUN cp ${APISERVER_BUILDER_FILE} /tmp/${APISERVER_BUILDER_FILE}
RUN tar -zvxf /tmp/${APISERVER_BUILDER_FILE} -C /apiserver-builder && rm -rf /tmp/${APISERVER_BUILDER_FILE}

ENV APISERVER_BUILDER_PATH=/apiserver-builder/bin
ENV PATH=${PATH}:${APISERVER_BUILDER_PATH}

# Experiment service section

ENV EXP_SVC_PATH=${GOPATH}/src/github.com/nervanasystems/carbon/applications/experiment-service
RUN mkdir -p ${EXP_SVC_PATH}
WORKDIR ${EXP_SVC_PATH}

ADD ./ ./

RUN yum -y install make
RUN make build

FROM centos:7.4.1708

COPY --from=build /build/work/src/github.com/nervanasystems/carbon/applications/experiment-service/dist/apiserver /apiserver
COPY --from=build /build/work/src/github.com/nervanasystems/carbon/applications/experiment-service/dist/controller-manager /controller-manager
