# https://github.com/kubernetes-retired/contrib/tree/master/startup-script
ARG BASE_IMAGE=centos:7
FROM ${BASE_IMAGE}
COPY manage-startup-script.sh /
RUN chmod +x /manage-startup-script.sh
CMD /manage-startup-script.sh
