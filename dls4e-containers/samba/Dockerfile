ARG BASE_IMAGE=dls4e/python36
#ARG BASE_IMAGE=centos:7.4.1708
FROM ${BASE_IMAGE}

RUN yum clean all
RUN yum update -y
RUN yum install -y samba
RUN pip install pysmb

RUN curl http://repository.toolbox.nervana.sclab.intel.com/files/dumb-init -o /bin/dumb-init
RUN chmod +x /bin/dumb-init

RUN curl http://repository.toolbox.nervana.sclab.intel.com/files/jq-linux64 -o /bin/jq
RUN chmod +x /bin/jq

ADD http://repository.toolbox.nervana.sclab.intel.com/kubernetes/v1.10.0/linux/amd64/kubectl /bin/kubectl
RUN chmod +x /bin/kubectl

COPY samba-init.sh /bin
COPY samba-loop.sh /bin
COPY samba-create.sh /bin
COPY samba-create-user.sh /bin
COPY samba-create-pv.sh /bin
COPY smb.conf /etc/samba/smb.conf
COPY samba-health.sh /bin

RUN mkdir -vp /etc/secrets/samba-users
RUN chmod +x /bin/samba-*

EXPOSE 137/udp 138/udp 139 445

ENTRYPOINT ["/bin/dumb-init", "--"]
CMD ["/bin/samba-init.sh"]
