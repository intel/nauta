ARG BASE_IMAGE
ARG HELM_DATA_IMAGE
FROM ${HELM_DATA_IMAGE} as data
FROM ${BASE_IMAGE}

COPY --from=data /build-output/helm/tiller /

RUN chmod +x /tiller

CMD ["/tiller"]
