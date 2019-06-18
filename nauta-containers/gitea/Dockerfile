ARG DUMBINIT_DATA_IMAGE
ARG BASE_IMAGE=golang:1.12.1
FROM ${DUMBINIT_DATA_IMAGE} as dumbinitdata
FROM ${BASE_IMAGE}

ADD gitea-v1.6.1.tar.gz ${GOPATH}/src/code.gitea.io/
RUN mv ${GOPATH}/src/code.gitea.io/gitea-1.6.1 ${GOPATH}/src/code.gitea.io/gitea

WORKDIR ${GOPATH}/src/code.gitea.io/gitea

ENV PATH=$PATH:${GOPATH}/bin
RUN go get -u github.com/jteeuwen/go-bindata/go-bindata && make clean generate build

EXPOSE 22 3000

RUN groupadd \
    --system --gid 1000 \
    git && \
  adduser \
    --system --no-create-home \
    --home /data/git \
    --shell /bin/bash \
    --uid 1000 \
    -g git \
    git && \
  echo "git:$(dd if=/dev/urandom bs=24 count=1 status=none | base64)" | chpasswd

ENV USER git
ENV GITEA_CUSTOM /data/gitea

VOLUME ["/data"]

RUN mkdir -p ${GOPATH}/src/code.gitea.io/gitea/conf && \
    cp -r ${GOPATH}/src/code.gitea.io/gitea/options/* ${GOPATH}/src/code.gitea.io/gitea/conf
RUN cp -r ${GOPATH}/src/code.gitea.io/gitea/docker/* /

RUN yum update -y && \
    yum install -y util-linux su-exec openssh-server && \
    yum clean all

RUN mkdir -p /app/gitea && cp ${GOPATH}/src/code.gitea.io/gitea/gitea /app/gitea/gitea

COPY --from=dumbinitdata /build-output/dumb-init /bin/dumb-init
COPY --from=dumbinitdata /build-output/dumb-init /usr/bin/dumb-init
RUN ln -s /app/gitea/gitea /usr/local/bin/gitea
COPY --from=dumbinitdata /build-output/dumb-init /dumb-init
RUN chmod +x /bin/dumb-init /usr/bin/dumb-init /dumb-init

COPY start.sh /
RUN chmod +x /start.sh
ADD sshd_config /etc/ssh/
ENTRYPOINT ["/bin/dumb-init", "/bin/bash", "-x", "/start.sh"]
