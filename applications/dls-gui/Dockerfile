FROM centos:7.5.1804

RUN curl --silent --location https://rpm.nodesource.com/setup_8.x | bash -
RUN yum -y install nodejs bzip2 gcc

ENV NODE_TLS_REJECT_UNAUTHORIZED 0

ADD package.json /app/
WORKDIR /app

RUN npm install
ADD . /app
RUN npm run build

# remove blacklisted components
RUN rm -rf ./node_modules/commander

EXPOSE 9000

WORKDIR /app
ENTRYPOINT ["node", "./api/server.js"]
