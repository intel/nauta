ARG BASE_IMAGE=shared/centos/rpm-packer
ARG PYTHON2_PIP_RPM_IMAGE=shared/build/rpm/python2-pip

FROM ${PYTHON2_PIP_RPM_IMAGE} as python2_pip_rpm_image
FROM ${BASE_IMAGE}

ENV RPM_VERSION=2.7
ENV RPM_RELEASE=0

RUN yum update -y && yum install -y python-devel python libffi-devel openssl-devel gcc gcc-c++
RUN curl "https://bootstrap.pypa.io/get-pip.py" | python && pip install -U pip==19.0.3 virtualenv==16.0.0 setuptools==39.2.0 wheel==0.31.1

ADD ./*.spec ./SPECS/

RUN build-rpm.sh pip-repository ${OUTPUT}/

COPY --from=python2_pip_rpm_image /out/* ${OUTPUT}/
