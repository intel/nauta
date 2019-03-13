# This dockerfile builds an Ansible binary for offline installer
ARG BASE_IMAGE=centos:7.6.1810
FROM ${BASE_IMAGE}

RUN yum update -y &&  yum install -y centos-release-scl && yum install -y devtoolset-7-gcc* libffi-devel gcc rh-python36

ADD requirements.txt /requirements.txt

ENV PATH=/opt/rh/rh-python36/root/usr/bin:$PATH
ENV LD_LIBRARY_PATH=/opt/rh/rh-python36/root/usr/lib64:$LD_LIBRARY_PATH
ENV MANPATH=/opt/rh/rh-python36/root/usr/share/man:$MANPATH
ENV PKG_CONFIG_PATH=/opt/rh/rh-python36/root/usr/lib64/pkgconfig:$PKG_CONFIG_PATH
ENV XDG_DATA_DIRS=/opt/rh/rh-python36/root/usr/share:$XDG_DATA_DIRS

RUN source /opt/rh/devtoolset-7/enable && \
            python3.6 -m pip install pip==19.0.3 virtualenv==16.0.0 setuptools==39.2.0 wheel==0.31.1

RUN source /opt/rh/devtoolset-7/enable && pip3.6 install -U virtualenv

# Red Hat compatibility
RUN ln -fs /opt/rh/rh-python36/root/usr/lib64/libpython3.so.rh-python36 /opt/rh/rh-python36/root/usr/lib64/libpython3.6mu.so.1.0 && \
    ln -fs /opt/rh/rh-python36/root/usr/lib64/libpython3.6m.so /opt/rh/rh-python36/root/usr/lib64/libpython3.6m.so.1.0 && \
    ln -fs /opt/rh/rh-python36/root/usr/lib64/libpython3.6m.so.rh-python36-1.0 /opt/rh/rh-python36/root/usr/lib64/libpython3.6.so.1.0


RUN source /opt/rh/devtoolset-7/enable && mkdir -p /out && virtualenv -p python3.6 /venv && /venv/bin/pip3.6 install -Ur /requirements.txt
RUN source /opt/rh/devtoolset-7/enable && /venv/bin/pip3.6 install -U pyinstaller && \
    /venv/bin/pyinstaller \
    -F "/venv/bin/ansible-playbook" \
    -n "ansible-playbook" \
    --specpath "/venv" \
    --clean \
    --distpath "/out/" \
    --hidden-import "jmespath" \
    --hidden-import "ansible" \
    --hidden-import "docker" \
    --hidden-import "configparser" \
    --hidden-import "netaddr" \
    --hidden-import "smtplib" \
    --hidden-import "logging.handlers" \
    --hidden-import "pty" \
    --hidden-import "crypt" \
    --hidden-import "xml.etree" \
    --hidden-import "xml.etree.ElementTree" \
    --add-data /venv/lib/python3.6/site-packages/ansible:ansible \
    --exclude-module readline
