ARG BASE_IMAGE
ARG METRICS_IMAGE
FROM ${METRICS_IMAGE} as metrics
FROM ${BASE_IMAGE}

ENV TENSORFLOW_VERSION=1.12.0
ENV HOROVOD_VERSION=0.16.2

RUN wget https://storage.googleapis.com/intel-optimized-tensorflow/tensorflow-${TENSORFLOW_VERSION}-cp27-cp27mu-linux_x86_64.whl -O /tensorflow-${TENSORFLOW_VERSION}-cp27-cp27mu-linux_x86_64.whl

COPY --from=metrics /build-output/experiment_metrics-*.tar.gz /

RUN wget https://github.com/Yelp/dumb-init/releases/download/v1.2.2/dumb-init_1.2.2_amd64.deb
RUN dpkg -i dumb-init_*.deb

RUN pip install --no-cache-dir --force-reinstall /tensorflow-${TENSORFLOW_VERSION}-*.whl && \
    pip install --ignore-installed /experiment_metrics-*.tar.gz

RUN apt-get update && apt-get install -y libopenmpi-dev openmpi-bin libhdf5-openmpi-dev

RUN pip install horovod==${HOROVOD_VERSION}

ENV MPIRUN_BIN /usr/bin/mpirun
RUN mv ${MPIRUN_BIN} ${MPIRUN_BIN}.real && \
    echo '#!/bin/bash' > ${MPIRUN_BIN} && \
    echo '${MPIRUN_BIN}.real --allow-run-as-root "$@"' >> ${MPIRUN_BIN} && \
    chmod a+x ${MPIRUN_BIN}

RUN echo "hwloc_base_binding_policy = none" >> /etc/openmpi/openmpi-mca-params.conf && \
    echo "rmaps_base_mapping_policy = slot" >> /etc/openmpi/openmpi-mca-params.conf

RUN apt-get install -y openssh-client openssh-server && \
    mkdir -p /var/run/sshd /app /root/.ssh

 # Allow OpenSSH to talk to containers without asking for confirmation
RUN cat /etc/ssh/ssh_config | grep -v StrictHostKeyChecking > /etc/ssh/ssh_config.new && \
    echo "    StrictHostKeyChecking no" >> /etc/ssh/ssh_config.new && \
    echo "    SendEnv LD_LIBRARY_PATH MPIRUN_BIN" >> /etc/ssh/ssh_config.new && \
    mv /etc/ssh/ssh_config.new /etc/ssh/ssh_config

RUN echo "AcceptEnv LD_LIBRARY_PATH MPIRUN_BIN" >> /etc/ssh/sshd_config

RUN echo "y" | ssh-keygen -N "" -f /root/.ssh/id_rsa && \
    cp /root/.ssh/id_rsa.pub /root/.ssh/authorized_keys && chmod og-rwx /root/.ssh/ -R

# Install kubectl
RUN apt-get install -y apt-transport-https
RUN curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
RUN echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | tee -a /etc/apt/sources.list.d/kubernetes.list
RUN apt-get update && apt-get install -y kubectl

