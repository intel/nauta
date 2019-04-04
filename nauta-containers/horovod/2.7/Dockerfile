ARG DUMBINIT_DATA_IMAGE
ARG KUBERNETES_DATA_IMAGE
ARG BASE_IMAGE
ARG METRICS_IMAGE
FROM ${DUMBINIT_DATA_IMAGE} as dumbinitdata
FROM ${KUBERNETES_DATA_IMAGE} as kubectl_data
FROM ${METRICS_IMAGE} as metrics
FROM ${BASE_IMAGE}

ENV TENSORFLOW_VERSION=1.13.1

# PIP shall == pip2.7 or pip3.6 and match paths below
RUN mkdir /pip2.7 /pip3.6
COPY intel_tensorflow-1.13.1-cp27-cp27mu-manylinux1_x86_64.whl /pip2.7
COPY intel_tensorflow-1.13.1-cp36-cp36m-manylinux1_x86_64.whl /pip3.6

COPY --from=metrics /build-output/experiment_metrics-*.tar.gz /

COPY --from=dumbinitdata /build-output/dumb-init /bin/dumb-init
COPY --from=dumbinitdata /build-output/dumb-init /usr/bin/dumb-init
COPY --from=dumbinitdata /build-output/dumb-init /dumb-init
RUN chmod +x /bin/dumb-init /usr/bin/dumb-init /dumb-init

RUN ls -lah /

RUN ${PIP} install --no-cache-dir --force-reinstall /${PIP}/intel_tensorflow*.whl && \
    ${PIP} install --ignore-installed /experiment_metrics-*.tar.gz
RUN yum clean all && \
    yum update -y && \
    yum install -y openmpi openmpi-devel gcc-c++ hdf5-devel gcc-gfortran python3-devel \
    python2-devel openblas-devel lapack-devel Cython cmake3 make git mercurial
RUN cp /usr/bin/cmake3 /usr/bin/cmake
RUN git config --global url."https://".insteadOf git://

ENV PATH=${PATH}:/usr/lib64/openmpi/bin
ENV LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/usr/lib64/openmpi/lib

RUN mkdir /horovod

COPY horovod-v0.15.2.tar.gz /horovod/
WORKDIR /horovod
RUN tar -xf horovod-v0.15.2.tar.gz
WORKDIR /horovod/horovod-0.15.2
RUN HOROVOD_WITHOUT_PYTORCH=1 python setup.py bdist_wheel
RUN ${PIP} install --no-cache-dir --no-clean --force-reinstall /horovod/horovod-0.15.2/dist/horovod-0.15.2-cp27-cp27mu-linux_x86_64.whl

ADD requirements.txt /horovod/
RUN ${PIP} install --no-binary :all: --ignore-installed scikit-build
RUN ${PIP} install -r /horovod/requirements.txt --no-binary :all: --no-clean --ignore-installed ipaddress

ENV MPIRUN_BIN /usr/lib64/openmpi/bin/mpirun
RUN mv ${MPIRUN_BIN} ${MPIRUN_BIN}.real && \
    echo '#!/bin/bash' > ${MPIRUN_BIN} && \
    echo '${MPIRUN_BIN}.real --allow-run-as-root "$@"' >> ${MPIRUN_BIN} && \
    chmod a+x ${MPIRUN_BIN}

RUN echo "hwloc_base_binding_policy = none" >> /etc/openmpi-x86_64/openmpi-mca-params.conf && \
    echo "rmaps_base_mapping_policy = slot" >> /etc/openmpi-x86_64/openmpi-mca-params.conf

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

# Install kubectl
COPY --from=kubectl_data /build-output/kubernetes/kubectl /bin/kubectl

RUN chmod +x /bin/kubectl

