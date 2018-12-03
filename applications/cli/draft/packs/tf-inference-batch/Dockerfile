FROM dls4e/tensorflow:1.9.0-py3

WORKDIR /app
ADD training.py .

ADD tf_serving_dls4e.sh /bin/tf_serving_dls4e
RUN chmod +x /bin/tf_serving_dls4e

ENV PYTHONUNBUFFERED 1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
