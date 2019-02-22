FROM ubuntu:18.04

RUN apt update && apt install wget -y
RUN wget -q -t 3 -O pandoc.deb https://github.com/jgm/pandoc/releases/download/2.6/pandoc-2.6-1-amd64.deb
RUN apt install ./pandoc.deb

ADD ["./", "/docs/"]

RUN ls
RUN pwd

RUN cd /docs && find . -name "*.md*" | while read file; do \
    pandoc -f markdown --template=.utils/template.html --toc --toc-depth=3 --standalone --lua-filter=.utils/links.lua \
    --metadata title="Nauta documentation" "$file" -o "${file%.*}.html"; done

RUN find /docs -name "*.md" -type f -delete

ARG BASE_IMAGE=centos:7.4.1708
FROM ${BASE_IMAGE}

COPY --from=0 /docs/user-guide /docs
COPY --from=0 /docs/.utils/uikit.css /docs/uikit.css
