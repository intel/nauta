ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ARG PYTHON_VERSION=2.7
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

RUN ${PIP} install --no-binary :all: --no-clean -U pip setuptools
RUN ${PIP} install --no-binary :all: --no-clean --ignore-installed scikit-build

RUN ${PIP} install \
        Pillow==5.4.* \
        h5py==2.9.* \
        ipykernel==4.10.* \
        jupyter==1.0.* \
        matplotlib==2.2.* \
        mock==2.0.* \
        numpy==1.16.* \
        scipy==1.2.* \
        scikit-learn==0.20.* \
        pandas==0.23.* \
        wheel==0.32.* \
        sklearn \
        tornado==4.5.3 \
        ptyprocess==0.5.0 \
        prompt-toolkit==1.0.15 \
        testpath==0.3.1 \
        nbconvert==4.3.0 \
        terminado==0.6 \
        notebook==4.3.2

RUN ${PYTHON} -m ipykernel.kernelspec
