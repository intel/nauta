DIRECTORY:=$(CURDIR)/../../
GLOBAL_WORKSPACE=$(CURDIR)/../../.workspace
WORKSPACE_NAME:=initializers
include $(CURDIR)/../../makelibs/commons.mk


init: PLAYBOOK=$(CURDIR)/initialize.yml
init: $(ACTIVATE)
	@echo $(BUILD_DIR)
	@$(ANSIBLE_PLAYBOOK_RUN) -e build_logs=$(BUILD_LOGS)
