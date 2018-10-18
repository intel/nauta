ARG TENSORFLOW_BUILD_IMAGE
ARG BASE_IMAGE
FROM ${TENSORFLOW_BUILD_IMAGE} as data
FROM ${BASE_IMAGE}

ENV TENSORFLOW_VERSION=1.9.0

COPY --from=data /build-output/tensorflow-${TENSORFLOW_VERSION}-*.whl /

RUN ${PIP} install --no-cache-dir --force-reinstall /tensorflow-${TENSORFLOW_VERSION}-*.whl
RUN ln -sf /usr/bin/python2 /usr/bin/python && yum clean all && yum install -y openmpi openmpi-devel gcc-c++

ENV PATH=${PATH}:/usr/lib64/openmpi/bin
ENV LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/usr/lib64/openmpi/lib

RUN mkdir /horovod

ADD requirements.txt /horovod/
RUN ${PIP} install -r /horovod/requirements.txt

ENV MPIRUN_BIN /usr/lib64/openmpi/bin/mpirun
RUN mv ${MPIRUN_BIN} ${MPIRUN_BIN}.real && \
    echo '#!/bin/bash' > ${MPIRUN_BIN} && \
    echo '${MPIRUN_BIN}.real --allow-run-as-root "$@"' >> ${MPIRUN_BIN} && \
    chmod a+x ${MPIRUN_BIN}

RUN echo "hwloc_base_binding_policy = none" >> /etc/openmpi-x86_64/openmpi-mca-params.conf && \
    echo "rmaps_base_mapping_policy = slot" >> /etc/openmpi-x86_64/openmpi-mca-params.conf && \
    echo "btl_tcp_if_exclude = lo,docker0" >> /etc/openmpi-x86_64/openmpi-mca-params.conf

RUN yum install -y openssh-clients openssh-server && \
    sshd-keygen && \
    mkdir -p /var/run/sshd /app /root/.ssh

 # Allow OpenSSH to talk to containers without asking for confirmation
RUN cat /etc/ssh/ssh_config | grep -v StrictHostKeyChecking > /etc/ssh/ssh_config.new && \
    echo "    StrictHostKeyChecking no" >> /etc/ssh/ssh_config.new && \
    echo "    SendEnv LD_LIBRARY_PATH MPIRUN_BIN" >> /etc/ssh/ssh_config.new && \
    mv /etc/ssh/ssh_config.new /etc/ssh/ssh_config

RUN echo "AcceptEnv LD_LIBRARY_PATH MPIRUN_BIN" >> /etc/ssh/sshd_config

RUN echo "export PATH=$PATH:/usr/lib64/openmpi/bin" >> /etc/bashrc

RUN echo "y" | ssh-keygen -N "" -f /root/.ssh/id_rsa && \
    cp /root/.ssh/id_rsa.pub /root/.ssh/authorized_keys && chmod og-rwx /root/.ssh/ -R

RUN ln -sf /opt/rh/rh-python36/root/usr/bin/${PYTHON} /usr/bin/python
