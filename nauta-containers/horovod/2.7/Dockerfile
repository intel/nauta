ARG TENSORFLOW_BUILD_IMAGE
ARG DUMBINIT_DATA_IMAGE
ARG KUBERNETES_DATA_IMAGE
ARG BASE_IMAGE
ARG METRICS_IMAGE
FROM ${TENSORFLOW_BUILD_IMAGE} as data
FROM ${DUMBINIT_DATA_IMAGE} as dumbinitdata
FROM ${KUBERNETES_DATA_IMAGE} as kubectl_data
FROM ${METRICS_IMAGE} as metrics
FROM ${BASE_IMAGE}

ENV TENSORFLOW_VERSION=1.14.0

COPY --from=data /build-output/tensorflow-${TENSORFLOW_VERSION}-*.whl /
COPY --from=metrics /build-output/experiment_metrics-*.tar.gz /
COPY --from=dumbinitdata /build-output/dumb-init /bin/dumb-init
COPY --from=dumbinitdata /build-output/dumb-init /usr/bin/dumb-init
COPY --from=dumbinitdata /build-output/dumb-init /dumb-init

RUN chmod +x /bin/dumb-init /usr/bin/dumb-init /dumb-init

RUN mkdir /tmp/openmpi
ADD openmpi-4.0.1.tar.gz /tmp/openmpi

RUN source /opt/rh/devtoolset-8/enable && ${PIP} install --no-cache-dir --force-reinstall /tensorflow-${TENSORFLOW_VERSION}-*.whl && \
    ${PIP} install --ignore-installed --no-cache-dir /experiment_metrics-*.tar.gz && \
    yum update -y && \
    yum install -y wget && \
    yum clean all && \
    git config --global url."https://".insteadOf git:// && \
    mkdir /horovod && \
    cd /tmp/openmpi && \
    cd openmpi-4.0.1 && \
    ./configure --enable-orterun-prefix-by-default && \
    make -j $(nproc) all && \
    make install && \
    ldconfig && \
    rm -rf /tmp/openmpi

# Create a wrapper for OpenMPI to allow running as root by default
RUN mv /usr/local/bin/mpirun /usr/local/bin/mpirun.real && \
    echo '#!/bin/bash' > /usr/local/bin/mpirun && \
    echo 'mpirun.real --allow-run-as-root "$@"' >> /usr/local/bin/mpirun && \
    chmod a+x /usr/local/bin/mpirun
# Create a wrapper for OpenMPI to allow running as root by default
RUN mv /usr/local/bin/mpirun /usr/local/bin/mpirun.real && \
    echo '#!/bin/bash' > /usr/local/bin/mpirun && \
    echo 'mpirun.real --allow-run-as-root "$@"' >> /usr/local/bin/mpirun && \
    chmod a+x /usr/local/bin/mpirun

ADD horovod-v0.16.4.tar.gz /horovod/
COPY requirements.txt /horovod/
WORKDIR /horovod/horovod
RUN source /opt/rh/devtoolset-8/enable && HOROVOD_WITHOUT_PYTORCH=1 python setup.py bdist_wheel && \
    ${PIP} install --no-cache-dir --force-reinstall /horovod/horovod/dist/horovod-0.16.4-cp27-cp27mu-linux_x86_64.whl && \
    ${PIP} install --no-binary=:all: --no-cache-dir --ignore-installed scikit-build && \
    ${PIP} install -r /horovod/requirements.txt --no-binary=:all: --no-cache-dir --ignore-installed ipaddress && \
    yum install -y openssh-clients openssh-server && \
    sshd-keygen && \
    mkdir -p /var/run/sshd /app /root/.ssh && \
    yum clean all

 # Allow OpenSSH to talk to containers without asking for confirmation
RUN cat /etc/ssh/ssh_config | grep -v StrictHostKeyChecking > /etc/ssh/ssh_config.new && \
    echo "    StrictHostKeyChecking no" >> /etc/ssh/ssh_config.new && \
    echo "    SendEnv LD_LIBRARY_PATH MPIRUN_BIN" >> /etc/ssh/ssh_config.new && \
    mv /etc/ssh/ssh_config.new /etc/ssh/ssh_config && \
    echo "AcceptEnv LD_LIBRARY_PATH MPIRUN_BIN" >> /etc/ssh/sshd_config && \
    echo "export PATH=$PATH:/usr/lib64/openmpi/bin" >> /etc/bashrc && \
    echo "y" | ssh-keygen -N "" -f /root/.ssh/id_rsa && \
    cp /root/.ssh/id_rsa.pub /root/.ssh/authorized_keys && chmod og-rwx /root/.ssh/ -R

# Install kubectl
COPY --from=kubectl_data /build-output/kubernetes/kubectl /bin/kubectl

RUN chmod +x /bin/kubectl

