FROM nauta/tensorflow-py2

WORKDIR /app

ENV PYTHONUNBUFFERED 1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

COPY training.py .
