ARG BASE_IMAGE
ARG DUMBINIT_DATA_IMAGE
FROM ${DUMBINIT_DATA_IMAGE} as dumbinitdata
FROM ${BASE_IMAGE}

COPY --from=dumbinitdata /build-output/dumb-init /bin/dumb-init
COPY --from=dumbinitdata /build-output/dumb-init /usr/bin/dumb-init

RUN chmod +x /bin/dumb-init /usr/bin/dumb-init

RUN mkdir -vp /fluentd/etc /fluentd/vendor/bundle

USER root
WORKDIR /home/fluent
ENV PATH /fluentd/vendor/bundle/ruby/2.3.0/bin:$PATH
ENV GEM_PATH /fluentd/vendor/bundle/ruby/2.3.0
ENV GEM_HOME /fluentd/vendor/bundle/ruby/2.3.0
ENV FLUENTD_DISABLE_BUNDLER_INJECTION 1

COPY ./conf/fluent.conf /fluentd/etc/
COPY ./conf/systemd.conf /fluentd/etc/
COPY ./conf/kubernetes.conf /fluentd/etc/
COPY Gemfile* /fluentd/

# Adjusted for CentOS, from:
#     https://github.com/fluent/fluentd-kubernetes-daemonset/blob/master/docker-image/v0.12/debian-elasticsearch/Dockerfile

RUN yum update -y && \
    yum install -y gcc gcc-c++ patch make libffi-devel openssl-devel rh-ruby23-ruby-devel && \
    yum clean all

RUN source /opt/rh/rh-ruby23/enable && gem install fluentd --version 1.2.5
RUN source /opt/rh/rh-ruby23/enable && gem install bundler --version 1.16.2
RUN source /opt/rh/rh-ruby23/enable &&  bundle config silence_root_warning true
RUN source /opt/rh/rh-ruby23/enable && bundle install --gemfile=/fluentd/Gemfile --path=/fluentd/vendor/bundle

COPY plugins /fluentd/plugins/
COPY entrypoint.sh /fluentd/entrypoint.sh

ENV FLUENTD_OPT=""
ENV FLUENTD_CONF="fluent.conf"

CMD ["/fluentd/entrypoint.sh"]

