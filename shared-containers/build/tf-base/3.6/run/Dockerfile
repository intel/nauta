ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ARG PYTHON_VERSION=3.6
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

RUN ln -s -f /usr/bin/${PYTHON} /usr/bin/python || true
RUN ln -s -f /usr/bin/${PIP} /usr/bin/pip || true

RUN ln -s -f /usr/bin/python3.6 /usr/bin/python3 || true
RUN ln -s -f /usr/bin/pip3.6 /usr/bin/pip3 || true

RUN ${PIP} install -U pip setuptools

RUN ${PIP} install \
        Pillow==5.4.* \
        h5py==2.9.* \
        ipykernel==5.1.* \
        jupyter==1.0.* \
        matplotlib==3.0.* \
        mock==2.0.* \
        numpy==1.16.* \
        scipy==1.2.* \
        scikit-learn==0.20.* \
        pandas==0.23.* \
        wheel==0.32.*

RUN ${PYTHON} -m ipykernel.kernelspec
