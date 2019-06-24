# Prepare nodejs with project files and without blacklisted components
ARG BASE_IMAGE
FROM ${BASE_IMAGE} as nauta_gui_nodejs_prod

RUN yum update -y && yum -y install rh-nodejs8 bzip2 gcc && yum clean all

ENV BLACKLISTED "ansicolors ansistyles archy buffer-equal-constant-time call-limit capture-stack-strace console-control-strings cyclist decode-uri-component fs.realpath genfun iferr imurmurhash isexe meant os-tmpdir promise-inflight qw read-cmd-shim sorted-union-stream umask wide_align yallist"
RUN cd /opt/rh/rh-nodejs8/root/usr/lib/node_modules/npm/node_modules/ && rm -rf $BLACKLISTED && cd /opt/rh/rh-nodejs8/root/usr/lib/node_modules/npm/node_modules.bundled/ && rm -rf $BLACKLISTED

ADD . /app
WORKDIR /app

# Prepare nodejs with project files
ARG BASE_IMAGE
FROM ${BASE_IMAGE} as nauta_gui_nodejs_dev

RUN yum update -y && yum -y install rh-nodejs8 bzip2 gcc && yum clean all
ADD . /app
WORKDIR /app

# Build gui client
FROM nauta_gui_nodejs_dev as nauta_gui_client_build

RUN source /opt/rh/rh-nodejs8/enable && npm install && npm run build

# Build backend
FROM nauta_gui_nodejs_dev as nauta_gui_backend_build

RUN source /opt/rh/rh-nodejs8/enable && npm install --only=prod

# Prepare prod image
FROM nauta_gui_nodejs_prod

ENV NODE_TLS_REJECT_UNAUTHORIZED 0

COPY --from=nauta_gui_client_build /app/dist /app/dist
COPY --from=nauta_gui_backend_build /app/node_modules /app/node_modules

EXPOSE 9000

WORKDIR /app

ENTRYPOINT [ "bash", "-c", "source /opt/rh/rh-nodejs8/enable && node ./api/server.js" ]
