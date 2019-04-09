ARG BASE_IMAGE=centos:7.6.1810
FROM ${BASE_IMAGE}

# add our user and group first to make sure their IDs get assigned consistently, regardless of whatever dependencies get added
RUN groupadd --system --gid 11211 memcache && useradd --system --gid memcache --uid 11211 memcache

RUN yum update -y && yum install memcached -y

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
RUN ln -s usr/local/bin/docker-entrypoint.sh /entrypoint.sh # backwards compat
ENTRYPOINT ["docker-entrypoint.sh"]

USER memcache
EXPOSE 11211

CMD ["memcached"]
