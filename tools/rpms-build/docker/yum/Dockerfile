ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum-carbon clean all
RUN yum-carbon install -y createrepo yum-utils python-dev python rpm-build python36u python36u-libs python36u-pip pigz
RUN pip3.6 install -U pip && pip3.6 install -U setuptools virtualenv wheel
RUN mkdir -p /root/rpm-build/BUILD \
    /root/rpmbuild/BUILDROOT \
    /root/rpmbuild/RPMS \
    /root/rpmbuild/SOURCES \
    /root/rpmbuild/SPECS \
    /root/rpmbuild/SRPMS

ADD build.sh /build.sh

RUN chmod +x build.sh

ADD download.sh /download.sh

RUN chmod +x download.sh
