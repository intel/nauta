ARG BASE_IMAGE
FROM ${BASE_IMAGE}

# Install development tools to install requirements. Only for redhat python

RUN yum install -y devtoolset-7-gcc*

RUN mkdir -p /out

ADD requirements.txt /out/requirements.txt

RUN source /opt/rh/devtoolset-7/enable && python3.6 -m pip download -d /out -r /out/requirements.txt
