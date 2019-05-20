ARG BASE_IMAGE
ARG METRICS_IMAGE
FROM ${METRICS_IMAGE} as metrics
FROM ${BASE_IMAGE}

ENV TENSORFLOW_VERSION=1.12.0
ENV HOROVOD_VERSION=0.16.2

RUN wget https://storage.googleapis.com/intel-optimized-tensorflow/tensorflow-${TENSORFLOW_VERSION}-cp36-cp36m-linux_x86_64.whl -O /tensorflow-${TENSORFLOW_VERSION}-cp36-cp36m-linux_x86_64.whl

COPY --from=metrics /build-output/experiment_metrics-*.tar.gz /

RUN pip install --no-cache-dir --force-reinstall /tensorflow-${TENSORFLOW_VERSION}-*.whl && \
    pip install --ignore-installed /experiment_metrics-*.tar.gz

RUN apt-get update && apt-get install -y build-essential

RUN mkdir /tmp/openmpi && \
    cd /tmp/openmpi && \
    wget https://www.open-mpi.org/software/ompi/v3.1/downloads/openmpi-3.1.2.tar.gz && \
    tar zxf openmpi-3.1.2.tar.gz && \
    cd openmpi-3.1.2 && \
    ./configure --enable-orterun-prefix-by-default && \
    make -j $(nproc) all && \
    make install && \
    ldconfig && \
    rm -rf /tmp/openmpi

RUN pip install horovod==${HOROVOD_VERSION}

# Create a wrapper for OpenMPI to allow running as root by default
RUN mv /usr/local/bin/mpirun /usr/local/bin/mpirun.real && \
    echo '#!/bin/bash' > /usr/local/bin/mpirun && \
    echo 'mpirun.real --allow-run-as-root "$@"' >> /usr/local/bin/mpirun && \
    chmod a+x /usr/local/bin/mpirun

# Configure OpenMPI to run good defaults:
#   --bind-to none --map-by slot --mca btl_tcp_if_exclude lo,docker0
RUN echo "hwloc_base_binding_policy = none" >> /usr/local/etc/openmpi-mca-params.conf && \
    echo "rmaps_base_mapping_policy = slot" >> /usr/local/etc/openmpi-mca-params.conf

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
