ARG DATA_IMAGE
ARG BASE_IMAGE
FROM ${DATA_IMAGE} as dataimage
FROM ${BASE_IMAGE}

COPY --from=dataimage /build-output/helm/tiller /
RUN chmod +x /tiller
ENTRYPOINT ["/tiller"]

