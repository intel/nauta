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

ENV TENSORFLOW_VERSION=1.13.1

COPY --from=data /build-output/tensorflow-${TENSORFLOW_VERSION}-*.whl /
COPY --from=metrics /build-output/experiment_metrics-*.tar.gz /
COPY --from=dumbinitdata /build-output/dumb-init /bin/dumb-init
COPY --from=dumbinitdata /build-output/dumb-init /usr/bin/dumb-init
COPY --from=dumbinitdata /build-output/dumb-init /dumb-init

RUN chmod +x /bin/dumb-init /usr/bin/dumb-init /dumb-init

RUN ${PIP} install --no-cache-dir --force-reinstall /tensorflow-${TENSORFLOW_VERSION}-*.whl && \
    ${PIP} install --ignore-installed --no-cache-dir /experiment_metrics-*.tar.gz && \
    yum update -y && \
    yum install -y openmpi openmpi-devel gcc-c++ hdf5-devel gcc-gfortran python3-devel \
    python2-devel openblas-devel lapack-devel Cython cmake3 make git && \
    yum clean all && \
    ln -s /usr/bin/cmake3 /usr/bin/cmake && \
    git config --global url."https://".insteadOf git:// && \
    mkdir /horovod

ENV PATH=${PATH}:/usr/lib64/openmpi/bin
ENV LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/usr/lib64/openmpi/lib
ENV MPIRUN_BIN /usr/lib64/openmpi/bin/mpirun

ADD horovod-v0.15.2.tar.gz /horovod/
COPY requirements.txt /horovod/
WORKDIR /horovod/horovod-0.15.2
RUN HOROVOD_WITHOUT_PYTORCH=1 python setup.py bdist_wheel && \
    ${PIP} install --no-cache-dir --force-reinstall /horovod/horovod-0.15.2/dist/horovod-0.15.2-cp27-cp27mu-linux_x86_64.whl && \
    ${PIP} install --no-binary=:all: --no-cache-dir --ignore-installed scikit-build && \
    ${PIP} install -r /horovod/requirements.txt --no-binary=:all: --no-cache-dir --ignore-installed ipaddress && \
    mv ${MPIRUN_BIN} ${MPIRUN_BIN}.real && \
    echo '#!/bin/bash' > ${MPIRUN_BIN} && \
    echo '${MPIRUN_BIN}.real --allow-run-as-root "$@"' >> ${MPIRUN_BIN} && \
    chmod a+x ${MPIRUN_BIN} && \
    echo "hwloc_base_binding_policy = none" >> /etc/openmpi-x86_64/openmpi-mca-params.conf && \
    echo "rmaps_base_mapping_policy = slot" >> /etc/openmpi-x86_64/openmpi-mca-params.conf && \
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

