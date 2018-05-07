VIRTUALENV_DIR:=$(CURDIR)/.venv
VIRTUALENV_BIN:=$(VIRTUALENV_DIR)/bin
ACTIVATE:=$(VIRTUALENV_BIN)/activate
REQUIREMENTS:=$(CURDIR)/requirements.txt

PIP:=$(VIRTUALENV_BIN)/pip
PYTHON:=$(VIRTUALENV_BIN)/python
ANSIBLE:=$(VIRTUALENV_BIN)/ansible
ANSIBLE_CFG:=$(CURDIR)/ansible.cfg
ANSIBLE_PLAYBOOK:=$(VIRTUALENV_BIN)/ansible-playbook
CONFIG:=$(CURDIR)/config.yml
LOCAL_INVENTORY:=$(CURDIR)/inventory/local

ANSIBLE_PLAYBOOK_RUN=. $(ACTIVATE); ANSIBLE_CONFIG=$(ANSIBLE_CFG) $(ANSIBLE_PLAYBOOK) \
                       -i $(ENV_INVENTORY) $(if $(ENV_CONFIG),-e @$(ENV_CONFIG) ,) \
                       $(PLAYBOOK)

TOOLBOX_HOME:=$(CURDIR)/toolbox

USER:=$(shell id -un)
USER_ID:=$(shell id -u)

$(VIRTUALENV_DIR):
	@virtualenv -p python3.6 $(VIRTUALENV_DIR)

$(ACTIVATE): $(VIRTUALENV_DIR) $(REQUIREMENTS)
	@$(PIP) install --upgrade-strategy only-if-needed -r $(REQUIREMENTS)
	@touch $(ACTIVATE)

ENV_%:
	@ if [ "${ENV_${*}}" = "" ]; then \
		echo "Environment variable ENV_$* is not set, please set one before run"; \
		exit 1; \
	fi

configured: ENV_INVENTORY

verify: PLAYBOOK=$(CURDIR)/verify.yml
verify: configured $(ACTIVATE)
	@$(ANSIBLE_PLAYBOOK_RUN) --tags verify

init: PLAYBOOK=$(CURDIR)/verify.yml
init: configured $(ACTIVATE)
	@$(ANSIBLE_PLAYBOOK_RUN) --tags init

install: PLAYBOOK=$(CURDIR)/dls.yml
install: configured $(ACTIVATE)
	@$(ANSIBLE_PLAYBOOK_RUN) --tags init,install
