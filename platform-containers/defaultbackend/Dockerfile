ARG INGRESS_DATA_IMAGE
ARG BASE_IMAGE
FROM ${INGRESS_DATA_IMAGE} as ingressdataimage
FROM ${BASE_IMAGE}

COPY --from=ingressdataimage /build-output/ingress/server /
RUN chmod +x /server

ENTRYPOINT ["/server"]

