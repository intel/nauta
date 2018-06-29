DIRECTORY:=$(CURDIR)
WORKSPACE_NAME:=chart-$(NAME)
include $(CURDIR)/../makelibs/commons.mk

configured: $(BUILD_DIR) ENV_OUTPUT ENV_BUILD_CONFIG

build: PLAYBOOK=$(CURDIR)/container.yml
build: configured $(ACTIVATE)
	@echo $(BUILD_DIR)
	@$(ANSIBLE_PLAYBOOK_RUN) -e output=$(ENV_OUTPUT) -e @$(ENV_BUILD_CONFIG) -e input_package=$(INPUT_PACKAGE)
