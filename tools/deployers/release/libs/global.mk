LIBS_DIRECTORY:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

include $(LIBS_DIRECTORY)/os-type-detect.mk

ANSIBLE_PLAYBOOK:=$(LIBS_DIRECTORY)/../bin/$(DLSE_OS)/$(DLSE_OS_NAME)/$(DLSE_OS_VERSION)/ansible-playbook
HELM:=$(LIBS_DIRECTORY)/../bin/$(DLSE_OS)/helm
KUBECTL:=$(LIBS_DIRECTORY)/../bin/$(DLSE_OS)/kubectl
LOADER:=$(LIBS_DIRECTORY)/../bin/$(DLSE_OS)/loader

ENV_%:
	@ if [ "${ENV_${*}}" = "" ]; then \
		echo "Environment variable ENV_$* is not set, please set one before run"; \
		exit 1; \
	fi

os-supported:
ifeq ($(DLSE_OS_SUPPORTED),1)
	@echo "Supported system: $(DLSE_OS) - $(DLSE_OS_ARCH) - $(DLSE_OS_NAME) - $(DLSE_OS_VERSION)"
else
	@echo "Unsupported system: $(DLSE_OS) - $(DLSE_OS_ARCH) bit - $(DLSE_OS_NAME) - $(DLSE_OS_VERSION)"
endif
