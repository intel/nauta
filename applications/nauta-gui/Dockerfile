ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum update -y && yum -y install rh-nodejs8 bzip2 gcc

ENV NODE_TLS_REJECT_UNAUTHORIZED 0

ADD package.json /app/
WORKDIR /app

RUN source /opt/rh/rh-nodejs8/enable && npm install
ADD . /app
RUN source /opt/rh/rh-nodejs8/enable && npm run build

# remove blacklisted components
RUN rm -rf /tmp/* ./node_modules/commander ./node_modules/phantomjs-prebuilt

EXPOSE 9000

WORKDIR /app

ENTRYPOINT [ "bash", "-c", "source /opt/rh/rh-nodejs8/enable && node ./api/server.js" ]

