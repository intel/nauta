ARG KUBERNETES_DATA_IMAGE
ARG BASE_IMAGE
FROM ${KUBERNETES_DATA_IMAGE} as data

FROM ${BASE_IMAGE}

RUN mkdir -p /out

COPY --from=data /build-output/kubernetes/kubectl /out/kubectl

RUN chmod +x /out/kubectl
