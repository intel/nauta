FROM nauta/tensorflow-py3

WORKDIR /app

ADD training.py .

ADD ps_entry.sh /bin/ps_entry
RUN chmod +x /bin/ps_entry

ENV PYTHONUNBUFFERED 1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
