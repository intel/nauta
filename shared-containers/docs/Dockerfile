FROM ubuntu:18.04
ARG DOCS_VERSION="develop"

RUN apt update && apt install wget -y
RUN wget -q -t 3 -O pandoc.deb https://github.com/jgm/pandoc/releases/download/2.6/pandoc-2.6-1-amd64.deb
RUN apt install ./pandoc.deb

ADD ["./", "/docs/"]

RUN ls
RUN pwd

RUN cd /docs && chmod +x .utils/convert_to_html.sh && .utils/convert_to_html.sh $DOCS_VERSION

RUN find /docs -name "*.md" -type f -delete

ARG BASE_IMAGE=centos:7.6.1810
FROM ${BASE_IMAGE}

COPY --from=0 /docs/user-guide /docs
COPY --from=0 /docs/.utils/uikit.css /docs/uikit.css
