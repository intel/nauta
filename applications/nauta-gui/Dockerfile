# Prepare nodejs with project files
ARG BASE_IMAGE
FROM ${BASE_IMAGE} as nauta_gui_nodejs

RUN yum update -y && yum -y install rh-nodejs8 bzip2 gcc
ADD . /app
WORKDIR /app

# Build gui client
FROM nauta_gui_nodejs as nauta_gui_client_build

RUN source /opt/rh/rh-nodejs8/enable && npm install && npm run build

# Copy client package && run backend
FROM nauta_gui_nodejs

ENV NODE_TLS_REJECT_UNAUTHORIZED 0

RUN source /opt/rh/rh-nodejs8/enable && npm install --only=prod

COPY --from=nauta_gui_client_build /app/dist /app/dist

EXPOSE 9000

WORKDIR /app

ENTRYPOINT [ "bash", "-c", "source /opt/rh/rh-nodejs8/enable && node ./api/server.js" ]

