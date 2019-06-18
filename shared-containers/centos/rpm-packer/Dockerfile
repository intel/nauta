ARG BASE_IMAGE=centos:7.6.1810
FROM ${BASE_IMAGE}
ARG USER_UID

ENV OUTPUT=/out

RUN yum install -y make curl wget unzip vim rpm-build createrepo pigz && \
    yum clean all

RUN adduser -u ${USER_UID} builder

RUN mkdir -p /root/rpmbuild/BUILD \
          /root/rpmbuild/RPMS \
          /root/rpmbuild/SOURCES \
          /root/rpmbuild/SPECS \
          /root/rpmbuild/SRPMS \
          /out && \
    chmod 777 /root      

WORKDIR /root/rpmbuild

COPY build-rpm.sh /usr/bin/
RUN chmod +x /usr/bin/build-rpm.sh
