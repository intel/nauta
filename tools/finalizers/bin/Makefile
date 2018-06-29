DIRECTORY:=$(CURDIR)
WORKSPACE_NAME:=finalizer-bin
include $(CURDIR)/../../makelibs/commons.mk

configured: ENV_PLATFORM_PACKAGE $(BUILD_DIR) ENV_OUTPUT

clean:
	if docker ps -a | grep release-builder- > /dev/null; then docker ps -a | grep release-builder- | cut -d ' ' -f 1 | xargs -n 128 docker rm -f; fi
	docker rm -rf $(BUILD_DIR)

build: PLAYBOOK=$(CURDIR)/container.yml
build: configured $(ACTIVATE)
	@echo $(BUILD_DIR)
	@$(ANSIBLE_PLAYBOOK_RUN) -e output=$(ENV_OUTPUT) -e package=$(ENV_PLATFORM_PACKAGE)
