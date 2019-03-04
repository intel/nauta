DIRECTORY:=$(CURDIR)
WORKSPACE_NAME:=finalizer-platform
include $(CURDIR)/../../makelibs/commons.mk

configured: ENV_PLATFORM_PACKAGE ENV_NAUTA_PACKAGE $(BUILD_DIR) ENV_OUTPUT ENV_BIN_PACKAGE ENV_DEPLOYER

build: PLAYBOOK=$(CURDIR)/container.yml
build: configured $(ACTIVATE)
	@echo $(BUILD_DIR)
	@$(ANSIBLE_PLAYBOOK_RUN) -e output=$(ENV_OUTPUT) -e platform_package=$(ENV_PLATFORM_PACKAGE) \
	-e nauta_package=$(ENV_NAUTA_PACKAGE) -e bin_package=$(ENV_BIN_PACKAGE) -e deployer=$(ENV_DEPLOYER)
