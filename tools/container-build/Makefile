DIRECTORY:=$(CURDIR)
WORKSPACE_NAME:=container
include $(CURDIR)/../makelibs/commons.mk

configured: ENV_BUILD_CONFIG $(BUILD_DIR) ENV_OUTPUT

build: PLAYBOOK=$(CURDIR)/container.yml
build: configured $(ACTIVATE)
	@echo $(BUILD_DIR)
	@$(ANSIBLE_PLAYBOOK_RUN) -e output=$(ENV_OUTPUT) -e input_package=$(INPUT_PACKAGE) -e build_logs=$(BUILD_LOGS) -e @$(ENV_BUILD_CONFIG) $(if $(BUILD_OPTIONS),-e @$(BUILD_OPTIONS),)
