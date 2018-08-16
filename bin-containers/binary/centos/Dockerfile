ARG PIP_IMAGE
ARG BASE_IMAGE
FROM ${PIP_IMAGE} as pip
FROM ${BASE_IMAGE}

COPY --from=pip /out/requirements.txt /requirements.txt

RUN pip3.6 install -U virtualenv

RUN mkdir -p /out && virtualenv -p python3.6 /venv && /venv/bin/pip install -Ur /requirements.txt
RUN /venv/bin/pip install -U pyinstaller && \
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
