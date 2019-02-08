FROM nauta/tensorflow-py2

# workdir set to /mnt - is treated by a jupyter as a main folder with notebooks
WORKDIR /mnt

ENV PYTHONUNBUFFERED 1
# setting PASSWORD env variable to an empty string turns off authetication
ENV PASSWORD ""

ADD training.py

ADD init_jupyter.sh /bin/init_jupyter
RUN chmod +x /bin/init_jupyter

# create dummy file to inform user about /mnt/input not being persistent volume
RUN ["mkdir", "/mnt/input"]
RUN echo "Warning - you are able to save some temporary content directly in the input directory. This content is discarded after the session ends." \
    > /mnt/input/README
CMD ["jupyter", "notebook", "--allow-root"]

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
