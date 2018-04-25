FROM centos
MAINTAINER rr

RUN yum update
RUN yum install -y samba

COPY samba-init.sh /bin
COPY samba-loop.sh /bin
COPY smb.conf /etc/samba/smb.conf

RUN mkdir -vp /etc/secrets/samba-users
RUN chmod +x /bin/samba-*

EXPOSE 137/udp 138/udp 139 445

ENTRYPOINT ["/bin/samba-init.sh"]
