DIRECTORY:=$(CURDIR)
WORKSPACE_NAME:=finalizer-platform
include $(CURDIR)/../../makelibs/commons.mk

configured: ENV_PLATFORM_PACKAGE $(BUILD_DIR) ENV_OUTPUT ENV_DEPLOYER ENV_CHART ENV_RPM_PACKAGE

build: PLAYBOOK=$(CURDIR)/container.yml
build: configured $(ACTIVATE)
	@echo $(BUILD_DIR)
	@$(ANSIBLE_PLAYBOOK_RUN) -e output=$(ENV_OUTPUT) -e deployer=$(ENV_DEPLOYER) -e package=$(ENV_PLATFORM_PACKAGE) -e chart=$(ENV_CHART) -e rpms=$(ENV_RPM_PACKAGE)
