ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum-carbon clean all
RUN yum-carbon install -y createrepo yum-utils python-dev python rpm-build python36u python36u-libs python36u-pip
RUN pip3.6 install -U pip && pip3.6 install -U setuptools virtualenv wheel
RUN mkdir -p /root/rpm-build/BUILD \
    /root/rpm-build/BUILDROOT \
    /root/rpm-build/RPMS \
    /root/rpm-build/SOURCES \
    /root/rpm-build/SPECS \
    /root/rpm-build/SRPMS
