ARG DATA_IMAGE
ARG BASE_IMAGE
FROM ${DATA_IMAGE} as dataimage
FROM ${BASE_IMAGE}

COPY --from=dataimage /build-output/etcd/etcd /usr/local/bin/
COPY --from=dataimage /build-output/etcd/etcdctl /usr/local/bin/
RUN chmod +x /usr/local/bin/etcd /usr/local/bin/etcdctl


