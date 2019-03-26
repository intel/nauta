FROM scratch as centos
ADD centos-docker.tar.xz /
RUN yum clean all && yum update -y && yum -y upgrade
FROM scratch
COPY --from=centos / /
CMD ["/bin/bash"]
