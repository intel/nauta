VIRTUALENV_DIR := $(CURDIR)/.venv
VIRTUALENV_BIN := $(VIRTUALENV_DIR)/bin
ACTIVATE := $(VIRTUALENV_BIN)/activate
REQUIREMENTS:=$(CURDIR)/requirements.txt

PIP := $(VIRTUALENV_BIN)/pip
PYTHON := $(VIRTUALENV_BIN)/PYTHON

TOOLBOX_HOME=$(CURDIR)/toolbox

USER := $(shell id -un)
USER_ID := $(shell id -u)

venv: $(ACTIVATE)

venv-clean:
	@rm -rf $(CURDIR)/.venv

K8S_%:
	@ if [ "${K8S_${*}}" = "" ]; then \
		echo "Environment variable K8S_$* is not set, please set one before run"; \
		exit 1; \
	fi

$(VIRTUALENV_DIR):
	@virtualenv -p python3.6 $(VIRTUALENV_DIR)

$(ACTIVATE): $(VIRTUALENV_DIR) $(REQUIREMENTS)
	@$(PIP) install --upgrade-strategy only-if-needed -r $(REQUIREMENTS)
	@touch $(ACTIVATE)

include toolbox/checks/checks.mk
include k8s-features/k8s-features.mk

k8s-installer-build:
	@(cd $(CURDIR)/platform-build && make yum-build)

dlsctl-build:
	@(cd $(CURDIR)/cli && make clean && make build)

unit-tests:
	@(cd $(CURDIR)/cli && make test)
