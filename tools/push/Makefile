DIRECTORY:=$(CURDIR)
WORKSPACE_NAME:=rpms
include $(CURDIR)/../makelibs/commons.mk

configured: ENV_S3_URL ENV_ACCESS_KEY ENV_SECRET_KEY ENV_SRC ENV_DEST

build: PLAYBOOK=$(CURDIR)/container.yml
build: configured $(ACTIVATE)
	@$(ANSIBLE_PLAYBOOK_RUN) -e s3_url=$(ENV_S3_URL) -e access_key=$(ENV_ACCESS_KEY) -e secret_key=$(ENV_SECRET_KEY) \
	-e src=$(ENV_SRC) -e dest=$(ENV_DEST) -e build_logs=$(BUILD_LOGS)
