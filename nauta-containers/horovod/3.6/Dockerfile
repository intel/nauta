ARG TENSORFLOW_BUILD_IMAGE
ARG KUBERNETES_DATA_IMAGE
ARG BASE_IMAGE
ARG METRICS_IMAGE
FROM ${TENSORFLOW_BUILD_IMAGE} as data
FROM ${METRICS_IMAGE} as metrics
FROM ${KUBERNETES_DATA_IMAGE} as kubectl_data
FROM ${BASE_IMAGE}

ENV TENSORFLOW_VERSION=1.14.0

COPY --from=data /build-output/tensorflow-${TENSORFLOW_VERSION}-*.whl /

COPY --from=metrics /build-output/experiment_metrics-*.tar.gz /

RUN source /opt/rh/rh-python36/enable && ${PIP} install --no-cache-dir --force-reinstall /tensorflow-${TENSORFLOW_VERSION}-*.whl
RUN source /opt/rh/devtoolset-8/enable && ${PIP} install --ignore-installed --no-cache-dir /experiment_metrics-*.tar.gz && \
    ln -sf /usr/bin/python2 /usr/bin/python && \
    yum update -y && \
    yum install -y wget && \
    yum clean all && \
    git config --global url."https://".insteadOf git:// && \
    mkdir /tmp/openmpi && \
    cd /tmp/openmpi && \
    wget https://download.open-mpi.org/release/open-mpi/v4.0/openmpi-4.0.1.tar.gz && \
    tar zxf openmpi-4.0.1.tar.gz && \
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

# Configure OpenMPI to run good defaults:
#   --bind-to none --map-by slot --mca btl_tcp_if_exclude lo,docker0
RUN echo "hwloc_base_binding_policy = none" >> /usr/local/etc/openmpi-mca-params.conf && \
    echo "rmaps_base_mapping_policy = slot" >> /usr/local/etc/openmpi-mca-params.conf

RUN mkdir /horovod
ADD horovod-v0.16.4.tar.gz /horovod/
WORKDIR /horovod/horovod
RUN source /opt/rh/devtoolset-8/enable && source /opt/rh/rh-python36/enable && ${PIP} install --no-binary=:all: --no-cache-dir --ignore-installed scikit-build setuptools rsa==3.4.2 
RUN source /opt/rh/devtoolset-8/enable && source /opt/rh/rh-python36/enable && HOROVOD_WITHOUT_PYTORCH=1 python3 setup.py bdist_wheel 
RUN source /opt/rh/devtoolset-8/enable && source /opt/rh/rh-python36/enable && ${PIP} install --no-cache-dir --force-reinstall /horovod/horovod/dist/horovod-0.16.4-cp36-cp36m-linux_x86_64.whl

COPY requirements.txt /horovod/

RUN source /opt/rh/devtoolset-8/enable && source /opt/rh/rh-python36/enable && ${PIP} install --no-binary=:all: --no-cache-dir --ignore-installed scikit-build setuptools

RUN source /opt/rh/devtoolset-8/enable && source /opt/rh/rh-python36/enable && ${PIP} install -r /horovod/requirements.txt --no-binary=:all: --no-cache-dir --ignore-installed ipaddress

RUN ln -sf /usr/bin/python2 /usr/bin/python && \
    yum install -y openssh-clients openssh-server && \
    yum clean all && \
    sshd-keygen && \
    mkdir -p /var/run/sshd /app /root/.ssh

 # Allow OpenSSH to talk to containers without asking for confirmation
RUN cat /etc/ssh/ssh_config | grep -v StrictHostKeyChecking > /etc/ssh/ssh_config.new && \
    echo "    StrictHostKeyChecking no" >> /etc/ssh/ssh_config.new && \
    echo "    SendEnv LD_LIBRARY_PATH MPIRUN_BIN" >> /etc/ssh/ssh_config.new && \
    mv /etc/ssh/ssh_config.new /etc/ssh/ssh_config && \
    echo "AcceptEnv LD_LIBRARY_PATH MPIRUN_BIN" >> /etc/ssh/sshd_config && \
    echo "y" | ssh-keygen -N "" -f /root/.ssh/id_rsa && \
    cp /root/.ssh/id_rsa.pub /root/.ssh/authorized_keys && chmod og-rwx /root/.ssh/ -R

# set python3 as python - this is *bad*, but this flow was tested.
# rr: I'd prefer to call source proper /opt/rh script on every use.
RUN ln -sf /opt/rh/rh-python36/root/usr/bin/${PYTHON} /usr/bin/python

# Install kubectl
COPY --from=kubectl_data /build-output/kubernetes/kubectl /bin/kubectl

RUN chmod +x /bin/kubectl
