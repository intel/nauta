FROM centos:7.5.1804
RUN mkdir -p /out
RUN yum update -y && yum install -y wget
RUN wget --quiet https://storage.googleapis.com/kubernetes-helm/helm-v2.11.0-linux-amd64.tar.gz -O ./helm-amd64.tar.gz
RUN tar -xvf ./helm-amd64.tar.gz
RUN cp ./linux-amd64/helm /out/helm
RUN chmod +x /out/helm
