ARG KUBERNETES_DATA_IMAGE
ARG DUMBINIT_DATA_IMAGE
ARG JQ_DATA_IMAGE
ARG BASE_IMAGE=nauta/python36
FROM ${JQ_DATA_IMAGE} as jqdata
FROM ${DUMBINIT_DATA_IMAGE} as dumbinitdata
FROM ${KUBERNETES_DATA_IMAGE} as kubectldata
FROM ${BASE_IMAGE}




RUN yum clean all && \
    yum update -y && \
    yum install -y samba
RUN pip install --no-binary :all: --no-clean pysmb

COPY --from=dumbinitdata /build-output/dumb-init /bin/dumb-init
RUN chmod +x /bin/dumb-init

COPY --from=jqdata /build-output/jq /bin/jq
RUN chmod +x /bin/jq

COPY --from=kubectldata /build-output/kubernetes/kubectl /bin/kubectl
RUN chmod +x /bin/kubectl

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

ENTRYPOINT ["/bin/dumb-init", "--"]
CMD ["/bin/samba-init.sh"]
