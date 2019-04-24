ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum update -y && \
    yum install -y devtoolset-8-gcc*

RUN source /opt/rh/devtoolset-8/enable && pip3.6 install elasticsearch-curator==5.6.0 boto3==1.9.134 cryptography==2.6.1 pyOpenSSL==19.0.0 && \
    sed -i '/import sys/a urllib3.contrib.pyopenssl.inject_into_urllib3()' /opt/rh/rh-python36/root/usr/bin/curator && \
    sed -i '/import sys/a import urllib3.contrib.pyopenssl' /opt/rh/rh-python36/root/usr/bin/curator && \
    sed -i '/import sys/a import urllib3' /opt/rh/rh-python36/root/usr/bin/curator

USER nobody:nobody

ENV LC_ALL=en_US.utf8
ENV LANG=en_US.utf8

ENTRYPOINT ["/opt/rh/rh-python36/root/usr/bin/curator"]
