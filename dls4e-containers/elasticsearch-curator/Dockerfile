ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN pip install elasticsearch-curator==5.5.4  boto3==1.4.8 requests-aws4auth==0.9 cryptography==2.1.3 pyOpenSSL==17.5.0 && \
 sed -i '/import sys/a urllib3.contrib.pyopenssl.inject_into_urllib3()' /usr/bin/curator && \
 sed -i '/import sys/a import urllib3.contrib.pyopenssl' /usr/bin/curator && \
 sed -i '/import sys/a import urllib3' /usr/bin/curator

USER nobody:nobody

ENV LC_ALL=en_US.utf8
ENV LANG=en_US.utf8

ENTRYPOINT ["/usr/bin/curator"]
