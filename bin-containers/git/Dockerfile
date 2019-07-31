FROM ubuntu:16.04

#set proxies if needed
#ARG http_proxy=<protocole://address:port>
#ARG https_proxy=<protocole://address:port>
#ARG HTTP_PROXY=<protocole://address:port>
#ARG HTTPS_PROXY=<protocole://address:port>

RUN apt-get update -y && apt-get install -y make libssl-dev gcc libcurl4-openssl-dev libexpat-dev gettext zlib1g-dev autoconf unzip git

WORKDIR /git_build

#uses sources stored in internal storage
RUN curl http://repository.toolbox.nervana.sclab.intel.com/NAUTA/downloads/git/git-sources-v2.22.0.zip -o /git_build/git-sources-v2.22.0.zip

RUN unzip git-sources-v2.22.0.zip

RUN cd git-master && autoconf && ./configure && make all && make strip

ARG FILES_TO_BE_COPIED="git git-add* git-checkout* git-clone git-commit* git-config git-fetch* git-ls-remote git-push git-pull git-remote* git-reset git-tag"

RUN mkdir git-binary && cd git-master && cp $FILES_TO_BE_COPIED ../git-binary/

#git build is stored in /git_build/git-v2.22.0-linux-amd64.tar.gz file inside of container
RUN cd git-binary && tar -cvzf ../git-v2.22.0-linux-amd64.tar.gz .
