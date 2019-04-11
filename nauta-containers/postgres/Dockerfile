#
# example Dockerfile for https://docs.docker.com/engine/examples/postgresql_service/
# modified for CentOS

ARG BASE_IMAGE
ARG DUMBINIT_DATA_IMAGE

FROM ${DUMBINIT_DATA_IMAGE} as dumbinitdata
FROM ${BASE_IMAGE}

COPY --from=dumbinitdata /build-output/dumb-init /bin/dumb-init
RUN chmod +x /bin/dumb-init

# ADD postgres user with fixed id
RUN useradd postgres -u 1234

RUN yum -y install postgresql postgresql-server postgresql-contrib; yum clean all

ENV PGDATA /var/lib/pgsql/data

# Expose the PostgreSQL port
EXPOSE 5432

# Replace systemctl and initialize postgres
ADD systemctl-replacement/systemctl.py /usr/bin/systemctl
RUN chmod +x /usr/bin/systemctl

# Add VOLUMEs to allow backup of config, logs and databases
VOLUME  ["/var/lib/pgsql/data"]

ADD postgres.sh /usr/bin/postgres.sh
RUN chmod +x /usr/bin/postgres.sh

ADD postgresql.conf /etc/postgresql.conf
ADD pg_hba.conf /etc/pg_hba.conf

#USER postgres
ENTRYPOINT ["/bin/dumb-init", "--"]

# Set the default command to run when starting the container
CMD ["/usr/bin/postgres.sh"]