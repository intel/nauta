ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum update -y && \
    yum install -y devtoolset-7-gcc*

RUN source /opt/rh/devtoolset-7/enable && pip3.6 install elasticsearch-curator==5.5.4 boto3==1.4.8 cryptography==2.1.3 pyOpenSSL==17.5.0 && \
    sed -i '/import sys/a urllib3.contrib.pyopenssl.inject_into_urllib3()' /opt/rh/rh-python36/root/usr/bin/curator && \
    sed -i '/import sys/a import urllib3.contrib.pyopenssl' /opt/rh/rh-python36/root/usr/bin/curator && \
    sed -i '/import sys/a import urllib3' /opt/rh/rh-python36/root/usr/bin/curator

USER nobody:nobody

ENV LC_ALL=en_US.utf8
ENV LANG=en_US.utf8

ENTRYPOINT ["/opt/rh/rh-python36/root/usr/bin/curator"]
