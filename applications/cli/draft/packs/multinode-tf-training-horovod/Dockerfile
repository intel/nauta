FROM nauta/horovod-py3

WORKDIR /app

ADD training.py .

ENV PYTHONUNBUFFERED 1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
