FROM dls4e/tensorflow:1.9.0-py3

# workdir set to /mnt - is treated by a jupyter as a main folder with notebooks
WORKDIR /mnt

ENV PYTHONUNBUFFERED 1
# setting PASSWORD env variable to an empty string turns off authetication
ENV PASSWORD ""

ADD training.py

CMD ["jupyter", "notebook", "--allow-root"]
