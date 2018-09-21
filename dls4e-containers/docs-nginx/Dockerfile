ARG BASE_IMAGE
ARG DOCS_IMAGE
FROM ${DOCS_IMAGE} as data
FROM ${BASE_IMAGE}

RUN mkdir /docs
COPY --from=data /docs/ /docs/

ADD nginx.conf /etc/nginx/nginx.conf
