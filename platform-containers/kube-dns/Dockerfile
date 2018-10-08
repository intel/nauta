ARG DATA_IMAGE
ARG BASE_IMAGE
FROM ${DATA_IMAGE} as dataimage
FROM ${BASE_IMAGE}

COPY --from=dataimage /build-output/addons/kube-dns /
RUN chmod +x /kube-dns

ENTRYPOINT /kube-dns
