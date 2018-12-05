ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum clean all && yum install -y which iproute2 net-tools iptables  make curl wget unzip vim rpm-build createrepo pigz libtool-ltdl-devel cmake glibc-static selinux-policy-devel

RUN mkdir -vp /build-output/rpm/
env GOPATH=/go
env PATH=$PATH:$GOPATH/bin
ADD docker-ce-18.06.0.ce-3.el7.centos.src.rpm /

RUN rpm --nomd5 -i /docker-ce-18.06.0.ce-3.el7.centos.src.rpm

WORKDIR ~/rpmbuild/SPECS
RUN ls -lah ~/rpmbuild/SPECS

RUN mkdir -vp /go/src/github.com/docker/

ADD docker-ce.spec /root/rpmbuild/SPECS/docker-ce-dls4e.spec

RUN rpmbuild --define="_origversion 18.06.1-ce" --define="_gitcommit e68fc71" --define="_version 18.06.0" --define="_release dls" -ba /root/rpmbuild/SPECS/docker-ce-dls4e.spec

RUN ls -Rlah /root/rpmbuild/RPMS/x86_64/

##### SELINUX SUPPORT ######################
#ADD docker-ce-selinux-17.03.3.ce-1.el7.src.rpm  /
#RUN rpm --nomd5 -i /docker-ce-selinux-17.03.3.ce-1.el7.src.rpm 
#WORKDIR ~/rpmbuild/SPECS
#RUN ls -lah ~/rpmbuild/SPECS
#RUN rpmbuild --define="_version 2.9" --define="_release dls"  -ba /root/rpmbuild/SPECS/docker-ce-selinux.spec
#RUN ls -Rlah /root/rpmbuild/RPMS/x86_64/
#RUN cp -vR /root/rpmbuild/RPMS/noarch/docker-ce-selinux-2.9-dls.noarch.rpm /build-output/rpm/docker-ce-selinux-2.9-dls.noarch.rpm
##### END OF SELINUX SUPPORT #############

RUN cp -vR /root/rpmbuild/RPMS/x86_64/docker-ce-18.06.0-dls.x86_64.rpm /build-output/rpm/docker-ce-18.06.0-dls.x86_64.rpm
RUN cp -vR /root/rpmbuild/RPMS/x86_64/docker-ce-debuginfo-18.06.0-dls.x86_64.rpm /build-output/rpm/docker-ce-debuginfo-18.06.0-dls.x86_64.rpm

ADD container-selinux-2.68-1.el7.noarch.rpm /build-output/rpm/

RUN ls -Rlah /build-output/rpm/

