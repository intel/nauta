FROM centos:7

RUN curl --silent --location https://rpm.nodesource.com/setup_8.x | bash -
RUN yum -y install nodejs bzip2 gcc

ADD package.json /app/
WORKDIR /app

RUN npm install
ADD . /app
RUN npm run build

EXPOSE 9000

WORKDIR /app
ENTRYPOINT ["node", "./api/server.js"]

