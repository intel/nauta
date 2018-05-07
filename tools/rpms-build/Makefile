DIRECTORY:=$(CURDIR)
WORKSPACE_NAME:=rpms
include $(CURDIR)/../makelibs/commons.mk

configured: ENV_BUILD_CONFIG $(BUILD_DIR) ENV_OUTPUT

build: PLAYBOOK=$(CURDIR)/container.yml
build: configured $(ACTIVATE)
	@echo $(BUILD_DIR)
	@$(ANSIBLE_PLAYBOOK_RUN) -e @$(ENV_BUILD_CONFIG) -e output=$(ENV_OUTPUT) $(if $(INCLUDED_FILES), -e included_files=$(INCLUDED_FILES),)
