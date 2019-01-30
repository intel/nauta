ARG PIP_IMAGE
ARG BASE_IMAGE
FROM ${PIP_IMAGE} as pip
FROM ${BASE_IMAGE}

RUN yum install -y devtoolset-7-gcc*

COPY --from=pip /out/requirements.txt /requirements.txt

RUN source /opt/rh/devtoolset-7/enable && pip3.6 install -U virtualenv

# Red Hat compatibility
RUN ln -fs /opt/rh/rh-python36/root/usr/lib64/libpython3.so.rh-python36 /opt/rh/rh-python36/root/usr/lib64/libpython3.6mu.so.1.0 && \
    ln -fs /opt/rh/rh-python36/root/usr/lib64/libpython3.6m.so /opt/rh/rh-python36/root/usr/lib64/libpython3.6m.so.1.0 && \
    ln -fs /opt/rh/rh-python36/root/usr/lib64/libpython3.6m.so.rh-python36-1.0 /opt/rh/rh-python36/root/usr/lib64/libpython3.6.so.1.0

RUN source /opt/rh/devtoolset-7/enable && mkdir -p /out && virtualenv -p python3.6 /venv && /venv/bin/pip3.6 install -Ur /requirements.txt
RUN source /opt/rh/devtoolset-7/enable && /venv/bin/pip3.6 install pip==18.1
RUN source /opt/rh/devtoolset-7/enable && /venv/bin/pip3.6 install -U pyinstaller==3.4 && \
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
