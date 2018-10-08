ARG DATA_IMAGE
ARG BASE_IMAGE
FROM ${DATA_IMAGE} as dataimage
FROM ${BASE_IMAGE}

COPY --from=dataimage /build-output/resizer/pod_nanny /
RUN chmod +x /pod_nanny

ENTRYPOINT /pod_nanny
