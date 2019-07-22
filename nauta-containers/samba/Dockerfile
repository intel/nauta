ARG BASE_IMAGE=nauta/python36
FROM ${BASE_IMAGE}

RUN yum clean all

ADD kubernetes.repo .
RUN cat kubernetes.repo >> /etc/yum.repos.d/kubernetes.repo

RUN yum update -y && yum install -y samba kubectl
RUN pip install dumb-init pysmb

COPY samba-init.sh /bin
COPY samba-loop.sh /bin
COPY samba-create.sh /bin
COPY samba-create-user.sh /bin
COPY samba-create-pv.sh /bin
COPY smb.conf /etc/samba/smb.conf
COPY samba-health.sh /bin
COPY samba-delete-users.sh /bin

RUN mkdir -vp /etc/secrets/samba-users
RUN chmod +x /bin/samba-*

EXPOSE 137/udp 138/udp 139 445

ENTRYPOINT ["/opt/rh/rh-python36/root/usr/bin/dumb-init", "--"]
CMD ["/bin/samba-init.sh"]
