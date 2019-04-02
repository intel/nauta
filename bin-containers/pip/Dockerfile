ARG BASE_IMAGE
FROM ${BASE_IMAGE}

# Install development tools to install requirements. Only for redhat python

RUN yum update -y && yum install -y devtoolset-8-gcc* libffi-devel gcc rh-python35

RUN mkdir -p /out

ADD requirements.txt /out/requirements.txt

RUN source /opt/rh/devtoolset-8/enable && python3.6 -m pip download -d /out -r /out/requirements.txt
RUN source /opt/rh/devtoolset-8/enable && python3.6 -m pip download --no-binary=:all: -d /out -r /out/requirements.txt

RUN source /opt/rh/devtoolset-8/enable && \
            export PATH=/opt/rh/rh-python35/root/usr/bin:$PATH && \
            export LD_LIBRARY_PATH=/opt/rh/rh-python35/root/usr/lib64:$LD_LIBRARY_PATH && \
            export MANPATH=/opt/rh/rh-python35/root/usr/share/man:$MANPATH && \
            export PKG_CONFIG_PATH=/opt/rh/rh-python35/root/usr/lib64/pkgconfig:$PKG_CONFIG_PATH && \
            export XDG_DATA_DIRS=/opt/rh/rh-python35/root/usr/share:$XDG_DATA_DIRS && \
            python3.5 -m pip install --no-binary :all: pip==19.0.3 virtualenv==16.0.0 setuptools==39.2.0 wheel==0.31.1

RUN source /opt/rh/devtoolset-8/enable && \
            export PATH=/opt/rh/rh-python35/root/usr/bin:$PATH && \
            export LD_LIBRARY_PATH=/opt/rh/rh-python35/root/usr/lib64:$LD_LIBRARY_PATH && \
            export MANPATH=/opt/rh/rh-python35/root/usr/share/man:$MANPATH && \
            export PKG_CONFIG_PATH=/opt/rh/rh-python35/root/usr/lib64/pkgconfig:$PKG_CONFIG_PATH && \
            export XDG_DATA_DIRS=/opt/rh/rh-python35/root/usr/share:$XDG_DATA_DIRS && \
            python3.5 -m pip download -d /out -r /out/requirements.txt

RUN source /opt/rh/devtoolset-8/enable && \
            export PATH=/opt/rh/rh-python35/root/usr/bin:$PATH && \
            export LD_LIBRARY_PATH=/opt/rh/rh-python35/root/usr/lib64:$LD_LIBRARY_PATH && \
            export MANPATH=/opt/rh/rh-python35/root/usr/share/man:$MANPATH && \
            export PKG_CONFIG_PATH=/opt/rh/rh-python35/root/usr/lib64/pkgconfig:$PKG_CONFIG_PATH && \
            export XDG_DATA_DIRS=/opt/rh/rh-python35/root/usr/share:$XDG_DATA_DIRS && \
            python3.5 -m pip download --no-binary=:all: -d /out -r /out/requirements.txt
