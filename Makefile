VIRTUALENV_DIR := $(CURDIR)/.venv
VIRTUALENV_BIN := $(VIRTUALENV_DIR)/bin
ACTIVATE := $(VIRTUALENV_BIN)/activate
REQUIREMENTS:=$(CURDIR)/requirements.txt

PIP := $(VIRTUALENV_BIN)/pip
PYTHON := $(VIRTUALENV_BIN)/python3

ANSIBLE_PLAYBOOK := $(VIRTUALENV_BIN)/ansible-playbook

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

ENV_%:
	@ if [ "${ENV_${*}}" = "" ]; then \
		echo "Environment variable ENV_$* is not set, please set one before run"; \
		exit 1; \
	fi

$(VIRTUALENV_DIR):
	@virtualenv -p python3.6 $(VIRTUALENV_DIR)

$(ACTIVATE): $(VIRTUALENV_DIR) $(REQUIREMENTS)
	@$(PIP) install --upgrade-strategy only-if-needed -r $(REQUIREMENTS)
	@touch $(ACTIVATE)

include toolbox/checks/checks.mk

k8s-installer-build:
	@make tools-release

nctl-build:
	@(cd $(CURDIR)/applications/cli && make full_clean && make push)

tools-%:
	@(cd $(CURDIR)/tools && make -j 2 $*)

single-tools-%:
	@(cd $(CURDIR)/tools && make $*)

unit-tests:
	@(cd $(CURDIR)/applications/cli && make test)

build-conditional-deep-clean:
	@(cd $(CURDIR)/applications/cli && make build-conditional-deep-clean)

cli-style:
	@(cd $(CURDIR)/applications/cli && make style)

unit-tests-with-code-cov:
	@(cd $(CURDIR)/applications/cli && make test-with-code-cov)

gui-unit-tests:
	@(cd $(CURDIR)/applications/nauta-gui && make test)

exp-service-tests:
	@(cd $(GOPATH)/src/github.com/nervanasystems/carbon/applications/experiment-service && make test)
	@(cd $(GOPATH)/src/github.com/nervanasystems/carbon/applications/experiment-service && make test_coverage)

include toolbox/providers/providers.mk
