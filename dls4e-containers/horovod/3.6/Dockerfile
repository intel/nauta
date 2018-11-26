ARG TENSORFLOW_BUILD_IMAGE
ARG KUBERNETES_DATA_IMAGE
ARG BASE_IMAGE
ARG METRICS_IMAGE
FROM ${TENSORFLOW_BUILD_IMAGE} as data
FROM ${METRICS_IMAGE} as metrics
FROM ${KUBERNETES_DATA_IMAGE} as kubectl_data
FROM ${BASE_IMAGE}

ENV TENSORFLOW_VERSION=1.9.0

COPY --from=data /build-output/tensorflow-${TENSORFLOW_VERSION}-*.whl /
COPY --from=metrics /build-output/experiment_metrics-*.tar.gz /

RUN source /opt/rh/rh-python36/enable && ${PIP} install --no-cache-dir --force-reinstall /tensorflow-${TENSORFLOW_VERSION}-*.whl && \
    ${PIP} install --ignore-installed /experiment_metrics-*.tar.gz

RUN ln -sf /usr/bin/python2 /usr/bin/python
RUN yum clean all && yum install -y openmpi openmpi-devel gcc-c++ hdf5-devel gcc-gfortran python3-devel python2-devel openblas-devel lapack-devel Cython cmake3 make git mercurial
RUN cp /usr/bin/cmake3 /usr/bin/cmake
RUN git config --global url."https://".insteadOf git://

#RUN ln -sf /opt/rh/rh-python36/root/usr/bin/${PYTHON} /usr/bin/python
ENV PATH=${PATH}:/usr/lib64/openmpi/bin
ENV LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/usr/lib64/openmpi/lib

RUN mkdir /horovod
COPY horovod-v0.15.1.tar.gz /horovod/
WORKDIR /horovod
RUN tar -xf horovod-v0.15.1.tar.gz
WORKDIR /horovod/horovod-0.15.1
RUN source /opt/rh/rh-python36/enable && ${PIP} install --no-binary :all: --ignore-installed scikit-build setuptools rsa==3.4.2
RUN source /opt/rh/rh-python36/enable && HOROVOD_WITHOUT_PYTORCH=1 python3 setup.py bdist_wheel
RUN source /opt/rh/rh-python36/enable && ${PIP} install --no-cache-dir --no-clean --force-reinstall /horovod/horovod-0.15.1/dist/horovod-0.15.1-cp36-cp36m-linux_x86_64.whl

ADD requirements.txt /horovod/
RUN source /opt/rh/rh-python36/enable && ${PIP} install --no-binary :all: --ignore-installed scikit-build setuptools
RUN source /opt/rh/rh-python36/enable && ${PIP} install -r /horovod/requirements.txt --no-binary :all: --no-clean --ignore-installed ipaddress

ENV MPIRUN_BIN /usr/lib64/openmpi/bin/mpirun
RUN mv ${MPIRUN_BIN} ${MPIRUN_BIN}.real && \
    echo '#!/bin/bash' > ${MPIRUN_BIN} && \
    echo '${MPIRUN_BIN}.real --allow-run-as-root "$@"' >> ${MPIRUN_BIN} && \
    chmod a+x ${MPIRUN_BIN}

RUN echo "hwloc_base_binding_policy = none" >> /etc/openmpi-x86_64/openmpi-mca-params.conf && \
    echo "rmaps_base_mapping_policy = slot" >> /etc/openmpi-x86_64/openmpi-mca-params.conf
RUN ln -sf /usr/bin/python2 /usr/bin/python
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

# set python3 as python - this is *bad*, but this flow was tested.
# rr: I'd prefer to call source proper /opt/rh script on every use.
RUN ln -sf /opt/rh/rh-python36/root/usr/bin/${PYTHON} /usr/bin/python

# Install kubectl
COPY --from=kubectl_data /build-output/kubernetes/kubectl /bin/kubectl

RUN chmod +x /bin/kubectl


