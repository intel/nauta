DIRECTORY:=$(CURDIR)
WORKSPACE_NAME:=finalizer-rpm
include $(CURDIR)/../../makelibs/commons.mk

configured: $(BUILD_DIR) ENV_RPM_PACKAGE ENV_OUTPUT ENV_BUILD_CONFIG

build: PLAYBOOK=$(CURDIR)/container.yml
build: configured $(ACTIVATE)
	@echo $(BUILD_DIR)
	@$(ANSIBLE_PLAYBOOK_RUN) -e output=$(ENV_OUTPUT) -e rpm_package=$(ENV_RPM_PACKAGE) -e platform_package=$(ENV_PLATFORM_PACKAGE) -e @$(ENV_BUILD_CONFIG)
