FROM nauta/tensorflow:1.9.0-py3

WORKDIR /app
ADD training.py .

ADD tf_serving_nauta.sh /bin/tf_serving_nauta
RUN chmod +x /bin/tf_serving_nauta

ENV PYTHONUNBUFFERED 1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
