LIBS_DIRECTORY:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

VIRTUALENV_DIR:=$(if $(GLOBAL_VIRTUALENV_DIR),$(GLOBAL_VIRTUALENV_DIR),$(DIRECTORY)/.venv)
VIRTUALENV_BIN:=$(VIRTUALENV_DIR)/bin
ACTIVATE:=$(VIRTUALENV_BIN)/activate
REQUIREMENTS:=$(LIBS_DIRECTORY)/../requirements.txt

PIP:=$(VIRTUALENV_BIN)/pip
PYTHON:=$(VIRTUALENV_BIN)/python
ANSIBLE:=$(VIRTUALENV_BIN)/ansible
ANSIBLE_CFG:=$(DIRECTORY)/ansible.cfg
ANSIBLE_PLAYBOOK:=$(VIRTUALENV_BIN)/ansible-playbook

WORKSPACE:=$(if $(GLOBAL_WORKSPACE),$(GLOBAL_WORKSPACE),$(CURDIR)/.workspace)

VENV_LOCK:=$(WORKSPACE)/.venv

WORKSPACE_BUILD:=$(WORKSPACE)/$(if $(WORKSPACE_NAME),$(WORKSPACE_NAME),default)

USER:=$(shell id -un)
USER_ID:=$(shell id -u)

GROUP:=$(shell id -gn)
GROUP_ID:=$(shell id -g)

### Build definitions
DEFAULT_NAME:=$(if $(NAME),$(NAME),$(if $(WORKSPACE_NAME),$(WORKSPACE_NAME),default))
DEFAULT_VERSION_MAJOR:=$(if $(VERSION_MAJOR),$(VERSION_MAJOR),1)
DEFAULT_VERSION_MINOR:=$(if $(VERSION_MINOR),$(VERSION_MINOR),0)
DEFAULT_VERSION_NO:=$(if $(VERSION_NO),$(VERSION_NO),0)
DEFAULT_VERSION_ID:=$(if $(VERSION_ID),$(VERSION_ID),$(shell TZ=UTC date '+%y%m%d%H%M%S'))
VERSION:=$(DEFAULT_VERSION_MAJOR).$(DEFAULT_VERSION_MINOR).$(DEFAULT_VERSION_NO)-$(DEFAULT_VERSION_ID)

BUILD_DIR:=$(WORKSPACE_BUILD)/$(VERSION)/$(DEFAULT_NAME)

ANSIBLE_PLAYBOOK_RUN=. $(ACTIVATE); ANSIBLE_CONFIG=$(ANSIBLE_CFG) $(ANSIBLE_PLAYBOOK) \
                       -i $(LIBS_DIRECTORY)/inventory --force-handlers -e default_ansible_python_interpreter=$(PYTHON) \
                       -e VERSION_NO=$(DEFAULT_VERSION_NO) -e VERSION_MINOR=$(DEFAULT_VERSION_MINOR) \
                       -e VERSION_MAJOR=$(DEFAULT_VERSION_MAJOR) -e VERSION_ID=$(DEFAULT_VERSION_ID) \
                       -e version=$(VERSION) -e user=$(USER) -e user_id=$(USER_ID) -e build_dir=$(BUILD_DIR) \
                       -e group=$(GROUP) -e group_id=$(GROUP_ID) -e build_name=$(DEFAULT_NAME) \
                       $(PLAYBOOK) -e @$(LIBS_DIRECTORY)/../config.yml

$(REQUIREMENTS_LOCK): $(WORKSPACE)
	@touch $(REQUIREMENTS_LOCK)

$(VENV_LOCK): $(WORKSPACE)
	@touch $(VENV_LOCK)

$(WORKSPACE):
	@mkdir -p $(WORKSPACE)
	@touch $(WORKSPACE)

$(WORKSPACE_BUILD): $(WORKSPACE)
	@mkdir -p $(WORKSPACE_BUILD)
	@touch $(WORKSPACE_BUILD)

$(BUILD_DIR): $(WORKSPACE_BUILD)
	@mkdir -p $(BUILD_DIR)
	@touch $(BUILD_DIR)

$(VIRTUALENV_DIR): $(VENV_LOCK)
	@flock $(VENV_LOCK) virtualenv -p python3.6 $(VIRTUALENV_DIR)

$(ACTIVATE): $(VIRTUALENV_DIR) $(REQUIREMENTS)
	@flock $(VENV_LOCK) $(PIP) install --upgrade-strategy only-if-needed -r $(REQUIREMENTS)
	@touch $(ACTIVATE)

ENV_%:
	@ if [ "${ENV_${*}}" = "" ]; then \
		echo "Environment variable ENV_$* is not set, please set one before run"; \
		exit 1; \
	fi
