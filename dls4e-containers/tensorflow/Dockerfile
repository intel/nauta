ARG TENSORFLOW_BUILD_IMAGE
ARG BASE_IMAGE
FROM ${TENSORFLOW_BUILD_IMAGE} as data
FROM ${BASE_IMAGE}

ENV TENSORFLOW_VERSION=1.9.0
ARG PYTHON_VERSION
ENV PYTHON=python${PYTHON_VERSION} PIP=pip${PYTHON_VERSION}

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

RUN ln -s -f /usr/bin/${PYTHON} /usr/bin/python
RUN ln -s -f /usr/bin/${PIP} /usr/bin/pip

RUN ln -s -f /usr/bin/python3.6 /usr/bin/python3
RUN ln -s -f /usr/bin/pip3.6 /usr/bin/pip3

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
