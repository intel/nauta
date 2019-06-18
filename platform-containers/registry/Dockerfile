ARG BASE_IMAGE
ARG BUILD_IMAGE
FROM ${BUILD_IMAGE}

RUN yum install -y which git && yum clean all

RUN mkdir -vp /build-output/registry \
              /build/gopath/src/

WORKDIR /build
ENV GOPATH=/build/gopath
ENV PATH=$PATH:$GOPATH/bin
RUN go get -v github.com/docker/distribution/cmd/registry
RUN cp /build/gopath/bin/* /build-output/registry/
RUN cd /build-output && \
    tar -I pigz -cf docker-registry.tar.gz registry/

FROM ${BASE_IMAGE}
WORKDIR /
RUN mkdir -vp /etc/docker/registry/
COPY --from=0 /build/gopath/bin/* /
COPY --from=0 /build/gopath/bin/* /bin/
RUN chmod +x /bin/registry /registry || true
COPY config.yml /etc/docker/registry/

ENTRYPOINT [ "/bin/registry", "serve", "/etc/docker/registry/config.yml" ]

