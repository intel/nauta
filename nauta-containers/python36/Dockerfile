ARG BASE_IMAGE=centos:7.4.1708
FROM ${BASE_IMAGE}

RUN yum clean all && yum update -y
#RUN yum install -y --skip-broken https://centos7.iuscommunity.org/ius-release.rpm

RUN echo $'[ius] \n\ 
name=IUS Community Packages for Enterprise Linux 7 - $basearch \n\ 
#baseurl=https://dl.iuscommunity.org/pub/ius/stable/CentOS/7/$basearch \n\
mirrorlist=https://mirrors.iuscommunity.org/mirrorlist?repo=ius-centos7&arch=$basearch&protocol=http \n\ 
failovermethod=priority \n\ 
enabled=1 \n\ 
gpgcheck=0 \n\ 
gpgkey=file:///etc/pki/rpm-gpg/IUS-COMMUNITY-GPG-KEY' > /etc/yum.repos.d/ius.repo


RUN yum install -y python36u python36u-pip python36u-devel
RUN pip3.6 install -U pip==10.0.1
