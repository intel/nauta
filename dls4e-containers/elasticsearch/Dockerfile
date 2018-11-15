ARG BUILD_IMAGE
ARG DUMBINIT_DATA_IMAGE
ARG BASE_IMAGE=dls4e/centos/java8
FROM ${DUMBINIT_DATA_IMAGE} as dumbinitdata

FROM ${BUILD_IMAGE} as build
FROM ${BASE_IMAGE}

EXPOSE 9200 9300

RUN yum clean all
RUN yum update -y
RUN yum install -y util-linux su-exec

COPY --from=dumbinitdata /build-output/dumb-init /bin/dumb-init
RUN chmod +x /bin/dumb-init

RUN mkdir -vp /elasticsearch 
COPY --from=build /build-output/archives/oss-tar/build/distributions/elasticsearch-*.tar.gz /

RUN rm -f rm -rf /etc/security/limits.d/20-nproc.conf

WORKDIR /elasticsearch
RUN tar --strip-components=1 -xf ../elasticsearch-*.tar.gz

ENV PATH /elasticsearch/bin:$PATH

RUN adduser --system  elasticsearch

RUN mkdir -vp /elasticsearch/config
RUN mkdir -vp /elasticsearch/config/scripts
RUN mkdir -vp /elasticsearch/plugin

RUN chown -R elasticsearch:elasticsearch /elasticsearch/config
RUN chown -R elasticsearch:elasticsearch /elasticsearch/config/scripts
RUN chown -R elasticsearch:elasticsearch /elasticsearch/plugin

COPY run.sh /
RUN chmod +x /run.sh

COPY config /elasticsearch/config
RUN chown -R elasticsearch:elasticsearch /elasticsearch/config

ENV ES_JAVA_OPTS "-Xms512m -Xmx512m"
ENV CLUSTER_NAME elasticsearch-default
ENV NODE_MASTER true
ENV NODE_DATA true
ENV NODE_INGEST true
ENV HTTP_ENABLE true
ENV NETWORK_HOST _site_
ENV HTTP_CORS_ENABLE true
ENV HTTP_CORS_ALLOW_ORIGIN *
ENV NUMBER_OF_MASTERS 1
ENV MAX_LOCAL_STORAGE_NODES 1
ENV SHARD_ALLOCATION_AWARENESS ""
ENV SHARD_ALLOCATION_AWARENESS_ATTR ""
ENV REPO_LOCATIONS ""

ENV DISCOVERY_SERVICE elasticsearch-discovery
ENV MEMORY_LOCK false

ENTRYPOINT ["/bin/dumb-init", "--"]
CMD ["/run.sh"]
