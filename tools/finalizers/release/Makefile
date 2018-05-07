DIRECTORY:=$(CURDIR)
WORKSPACE_NAME:=finalizer-platform
include $(CURDIR)/../../makelibs/commons.mk

configured: ENV_PLATFORM_PACKAGE ENV_DLS4E_PACKAGE $(BUILD_DIR) ENV_OUTPUT

build: PLAYBOOK=$(CURDIR)/container.yml
build: configured $(ACTIVATE)
	@echo $(BUILD_DIR)
	@$(ANSIBLE_PLAYBOOK_RUN) -e output=$(ENV_OUTPUT) -e platform_package=$(ENV_PLATFORM_PACKAGE) \
	-e dls4e_package=$(ENV_DLS4E_PACKAGE)
