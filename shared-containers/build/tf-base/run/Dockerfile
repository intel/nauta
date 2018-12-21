ARG PYTHON_VERSION

FROM python:${PYTHON_VERSION}

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

RUN pip install -U pip setuptools

RUN pip install \
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

RUN python -m ipykernel.kernelspec
