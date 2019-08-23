ARG BUILD_IMAGE
ARG DUMBINIT_DATA_IMAGE
ARG BASE_IMAGE=nauta/centos/java
FROM ${DUMBINIT_DATA_IMAGE} as dumbinitdata

FROM ${BUILD_IMAGE} as build
FROM ${BASE_IMAGE}

EXPOSE 9200 9300

RUN yum update -y && \
    yum install -y util-linux su-exec && \
    yum clean all

COPY --from=dumbinitdata /build-output/dumb-init /bin/dumb-init

RUN chmod +x /bin/dumb-init

RUN mkdir -vp /elasticsearch  \
              /elasticsearch/config/scripts \
              /elasticsearch/plugin

COPY --from=build /build-output/archives/oss-no-jdk-linux-tar/build/distributions/elasticsearch-*.tar.gz /

RUN printf '%s\t%s  %s\t%s\n%s\t%s  %s\t%s\n' 'elasticsearch' 'hard' 'nproc' '65536' 'elasticsearch' 'soft' 'nproc' '16384' >> /etc/security/limits.d/20-nproc.conf

WORKDIR /elasticsearch

RUN tar --strip-components=1 -xf ../elasticsearch-*.tar.gz && rm ../elasticsearch-*.tar.gz

ENV PATH /elasticsearch/bin:$PATH

RUN adduser --system -u 5000 elasticsearch && \
    mkdir -vp /elasticsearch/config/scripts /elasticsearch/plugin && \
    chown -R elasticsearch:elasticsearch /elasticsearch/config /elasticsearch/plugin

COPY run.sh /
RUN chmod +x /run.sh

COPY config /elasticsearch/config
RUN chown -R elasticsearch:elasticsearch /elasticsearch/config

ENV JAVA_HOME=/usr/lib/jvm/jre-1.8.0-openjdk \
    ES_JAVA_OPTS="-Xms512m -Xmx512m" \
    CLUSTER_NAME=elasticsearch-default \
    NODE_MASTER=true \
    NODE_DATA=true \
    NODE_INGEST=true \
    NETWORK_HOST=_site_ \
    HTTP_CORS_ENABLE=true \
    HTTP_CORS_ALLOW_ORIGIN=* \
    NUMBER_OF_MASTERS=1 \
    MAX_LOCAL_STORAGE_NODES=1 \
    SHARD_ALLOCATION_AWARENESS="" \
    SHARD_ALLOCATION_AWARENESS_ATTR="" \
    REPO_LOCATIONS="" \
    DISCOVERY_SERVICE=elasticsearch-discovery \
    MEMORY_LOCK=false

ENTRYPOINT ["/bin/dumb-init", "--"]
CMD ["/run.sh"]
