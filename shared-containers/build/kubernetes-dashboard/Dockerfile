ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum update -y && \
    yum -y install rh-nodejs8 bzip2 gcc which git \
                                    java-1.8.0-openjdk-devel java-1.8.0-openjdk \
                                    zip rsync curl pkg-config make libtool \
                                    libcurl patch automake patch gcc-c++ && \
    yum clean all

ENV NODE_TLS_REJECT_UNAUTHORIZED 0

# go section ####################################

RUN mkdir -p /build/work

ENV GO_VERSION=1.10.2
ENV GO_ARCH=amd64
ENV GO_OS=linux
ENV GO_FILE=go${GO_VERSION}.${GO_OS}-${GO_ARCH}.tar.gz

COPY ${GO_FILE} /tmp/${GO_FILE}
RUN tar -zvxf /tmp/${GO_FILE} -C /build && rm -rf /tmp/${GO_FILE}

ENV GOROOT=/build/go
ENV GOPATH=/build/work
ENV PATH=${PATH}:${GOROOT}/bin

RUN go get -u github.com/golang/dep/cmd/dep

################## end of go section ############

#### PROXY - some parts of dashboard build system hardcode git:// protocol,
###          which is not easy for proxies we have.
RUN git config --global url."https://github.com/".insteadOf git@github.com:
RUN git config --global url."https://".insteadOf git://
####################

COPY kubernetes-dashboard-v1.8.3.tar.gz /
RUN mkdir -vp ${GOPATH}/src/github.com/kubernetes/dashboard
WORKDIR ${GOPATH}/src/github.com/kubernetes/dashboard
RUN tar --strip-components=1 -xf /kubernetes-dashboard-v1.8.3.tar.gz
RUN source /opt/rh/rh-nodejs8/enable && npm install --unsafe-perm
RUN source /opt/rh/rh-nodejs8/enable && ./node_modules/gulp/bin/gulp.js build-frontend
RUN cp -Rv /build/work/src/github.com/kubernetes/dashboard/dist/amd64/* /

RUN go build github.com/kubernetes/dashboard/src/app/backend
RUN cp backend /dashboard

EXPOSE 9090 8443
ENTRYPOINT ["/dashboard", "--insecure-bind-address=0.0.0.0", "--bind-address=0.0.0.0"]
