ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum update -y && yum install -y which git glibc-static && yum clean all

RUN mkdir -vp /build/gopath/ \
              /build-output/addons \
              /build-output/resizer

ENV GOPATH=/build/gopath
WORKDIR /build/gopath

RUN git clone https://github.com/kubernetes/dns /build/gopath/src/k8s.io/dns && \
    git clone -b v1.15.3 https://github.com/kubernetes/kubernetes /build/gopath/src/k8s.io/kubernetes && \
    git clone -b cluster-autoscaler-1.13.6 https://github.com/kubernetes/autoscaler /build/gopath/src/k8s.io/autoscaler && \
    go get -v ./... || true && \
    go get -v ./... || true && \
    go get -v ./... || true && \
    cd /build/gopath/src/k8s.io/dns  && ARCH=amd64 VERSION=1.14.12-dirty PKG=k8s.io/dns bash -x ./build/build.sh && \
    go get github.com/tools/godep && \
    cd /build/gopath/src/k8s.io/autoscaler/addon-resizer && \
	CGO_ENABLED=0 go build -a -installsuffix cgo --ldflags '-w' -o /build-output/resizer/pod_nanny nanny/main/pod_nanny.go && \
    cd /build/gopath/src/k8s.io/kubernetes/build/pause && gcc -Os -Wall -Werror -static pause.c -o pause && \
    cd /build/gopath/src/k8s.io/kubernetes/build/pause && gcc -Os -Wall -Werror -static orphan.c -o orphan && \
    cp -v /build/gopath/src/k8s.io/kubernetes/build/pause/{pause,orphan} /build-output/ && \
    cp ${GOPATH}/bin/linux_amd64/* /build-output/addons/ && \
    cd /build-output && \
    tar -I pigz -cvf addons.tar.gz addons/ resizer/ pause orphan && \
    rm -rf /build
