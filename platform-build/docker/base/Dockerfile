ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN mkdir -p /etc/carbon/repos.d
ADD repo /etc/carbon/repos.d/local.repo
ADD yum.conf /etc/carbon/yum.conf

ENV YUM_CONF=/etc/carbon/yum.conf

ADD yum-carbon /bin/yum-carbon

RUN chmod +x /bin/yum-carbon
