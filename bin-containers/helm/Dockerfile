ARG HELM_DATA_IMAGE
ARG BASE_IMAGE
FROM ${HELM_DATA_IMAGE} as data

FROM ${BASE_IMAGE}

RUN mkdir -p /out

COPY --from=data /build-output/helm/helm /out/helm

RUN chmod +x /out/helm
