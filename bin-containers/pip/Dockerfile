ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN mkdir -p /out

ADD requirements.txt /out/requirements.txt

RUN python3.6 -m pip download -d /out -r /out/requirements.txt

RUN yum install -y libffi-devel gcc python35u python35u-devel python35u-pip
RUN python3.5 -m pip download -d /out -r /out/requirements.txt

RUN python3.6 -m pip download --no-binary=:all: -d /out -r /out/requirements.txt
RUN python3.5 -m pip download --no-binary=:all: -d /out -r /out/requirements.txt
