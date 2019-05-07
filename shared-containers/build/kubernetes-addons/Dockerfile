ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum clean all && yum update -y && yum install -y which git glibc-static

RUN mkdir -vp /build/gopath/
RUN mkdir -vp /build-output/addons /build-output/resizer
ENV GOPATH=/build/gopath
WORKDIR /build/gopath



RUN git clone https://github.com/kubernetes/dns        /build/gopath/src/k8s.io/dns 
RUN git clone -b release-1.11 https://github.com/kubernetes/kubernetes /build/gopath/src/k8s.io/kubernetes
RUN git clone -b cluster-autoscaler-release-1.12 https://github.com/kubernetes/autoscaler /build/gopath/src/k8s.io/autoscaler


RUN go get -v ./... || true
RUN go get -v ./... || true
RUN go get -v ./... || true

RUN cd /build/gopath/src/k8s.io/dns  && ARCH=amd64 VERSION=1.14.12-dirty PKG=k8s.io/dns bash -x ./build/build.sh && ls -lahR

RUN go get github.com/tools/godep
RUN cd /build/gopath/src/k8s.io/autoscaler/addon-resizer && \
	CGO_ENABLED=0 go build -a -installsuffix cgo --ldflags '-w' -o /build-output/resizer/pod_nanny nanny/main/pod_nanny.go

RUN cd /build/gopath/src/k8s.io/kubernetes/build/pause && gcc -Os -Wall -Werror -static pause.c -o pause
RUN cd /build/gopath/src/k8s.io/kubernetes/build/pause && gcc -Os -Wall -Werror -static orphan.c -o orphan
RUN cp -v /build/gopath/src/k8s.io/kubernetes/build/pause/{pause,orphan} /build-output/

RUN ls -lR ${GOPATH}/bin/linux_amd64

RUN mkdir -p /build-output/addons && \
    cp ${GOPATH}/bin/linux_amd64/* /build-output/addons/ && \
    cd /build-output && \
    tar -I pigz -cvf addons.tar.gz addons/ resizer/ pause orphan
