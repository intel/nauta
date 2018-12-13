ARG BASE_IMAGE
ARG KUBERNETES_DATA_IMAGE
FROM ${KUBERNETES_DATA_IMAGE} as data

FROM ${BASE_IMAGE}

COPY --from=data /build-output/kubernetes/kubectl /bin/kubectl

RUN chmod +x /bin/kubectl