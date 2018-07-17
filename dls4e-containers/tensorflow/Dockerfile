ARG TENSORFLOW_BUILD_IMAGE
ARG BASE_IMAGE
FROM ${TENSORFLOW_BUILD_IMAGE} as data
FROM ${BASE_IMAGE}

ENV TENSORFLOW_VERSION=1.9.0
ARG PYTHON_VERSION
ENV PYTHON=python${PYTHON_VERSION} PIP=pip${PYTHON_VERSION}

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libfreetype6-dev \
        libhdf5-serial-dev \
        libpng12-dev \
        libzmq3-dev \
        pkg-config \
        python \
        python3-pip \
        python-pip \
        python3-dev \
        python-dev \
        python-setuptools \
        rsync \
        software-properties-common \
        unzip \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY jupyter_notebook_config.py /root/.jupyter/

COPY notebooks /notebooks

COPY run_jupyter.sh /
RUN chmod +x /run_jupyter.sh

# TensorBoard
EXPOSE 6006
# IPython
EXPOSE 8888

WORKDIR "/notebooks"

CMD ["/run_jupyter.sh", "--allow-root"]

RUN ln -s -f /usr/bin/${PYTHON} /usr/bin/python && \
    ln -s -f /usr/bin/${PIP} /usr/bin/pip

RUN ${PIP} install -U pip setuptools

RUN ${PIP} install \
        Pillow \
        h5py \
        ipykernel \
        jupyter \
        matplotlib \
        mock \
        numpy \
        scipy \
        sklearn \
        pandas \
        wheel

RUN ${PYTHON} -m ipykernel.kernelspec

COPY --from=data /build-output/tensorflow-${TENSORFLOW_VERSION}-*.whl /

RUN ${PIP} install --no-cache-dir --force-reinstall /tensorflow-${TENSORFLOW_VERSION}-*.whl && \
    rm -rf /tensorflow-${TENSORFLOW_VERSION}-*.whl
