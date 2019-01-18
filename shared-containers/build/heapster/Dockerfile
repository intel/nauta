ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum clean all && yum install -y which

RUN mkdir /build-output/heapster

RUN mkdir -vp /build/gopath/src/k8s.io/heapster
COPY heapster-v1.4.3.tar.gz /build/
WORKDIR /build
RUN tar -xf heapster-v1.4.3.tar.gz --strip-components=1 -C /build/gopath/src/k8s.io/heapster/
ENV GOPATH=/build/gopath
ENV PATH=$PATH:$GOPATH/bin
WORKDIR /build/gopath/src/k8s.io/heapster
RUN ls -lah

# Workaround: we're using release, not git checkout: #
RUN sed -i '15s/.*/GIT_COMMIT:=NAUTA/' Makefile
######################################################

RUN make build
RUN ls -lah
RUN cp -v heapster /build-output/heapster/
RUN cp -v eventer  /build-output/heapster/
RUN cd /build-output && \
    tar -I pigz -cf heapster.tar.gz heapster/
