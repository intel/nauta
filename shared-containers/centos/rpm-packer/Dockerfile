ARG BASE_IMAGE=centos:7.4.1708
FROM ${BASE_IMAGE}

# RUN adduser -u ${USER_UID} builder

RUN yum clean all && \
    yum update -y && \
    yum install -y make curl wget unzip vim rpm-build createrepo pigz

RUN mkdir /root/rpmbuild/BUILD \
          /root/rpmbuild/RPMS \
          /root/rpmbuild/SOURCES \
          /root/rpmbuild/SPECS \
          /root/rpmbuild/SRPMS -p

RUN ls -ln
RUN chmod 777 /root
#RUN false

WORKDIR /root/rpmbuild

ADD build-rpm.sh /usr/bin/
RUN chmod +x /usr/bin/build-rpm.sh

ENV OUTPUT=/out

RUN mkdir ${OUTPUT}
