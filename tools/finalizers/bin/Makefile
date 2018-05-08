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
	@$(ANSIBLE_PLAYBOOK_RUN) -e output=$(ENV_OUTPUT) -e platform_package=$(ENV_PLATFORM_PACKAGE) \
	-e dls4e_package=$(ENV_DLS4E_PACKAGE) || RET=$$? && \
	if docker ps -a | grep release-builder-$(VERSION) > /dev/null; then docker ps -a | grep release-builder-$(VERSION) | cut -d ' ' -f 1 | xargs -n 128 docker rm -f; fi && \
	rm -rf $(BUILD_DIR) && exit $$RET
