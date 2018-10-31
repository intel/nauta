ARG DATA_IMAGE
ARG BASE_IMAGE
FROM ${DATA_IMAGE} as dataimage
FROM ${BASE_IMAGE}

COPY --from=dataimage /dashboard /
RUN chmod +x /dashboard
COPY --from=dataimage /public/ /public/
COPY --from=dataimage /locale_conf.json /
RUN ls -lah

WORKDIR /
ENTRYPOINT ["/dashboard", "--insecure-bind-address=0.0.0.0", "--bind-address=0.0.0.0"]

