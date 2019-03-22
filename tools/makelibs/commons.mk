LIBS_DIRECTORY:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

# OS detection
UNAME:=$(shell uname)
ifeq ($(findstring MSYS_NT-10.0,$(UNAME)),MSYS_NT-10.0)
OS:=Windows
endif
ifeq ($(findstring Linux,$(UNAME)),Linux)
OS:=Linux
endif
ifeq ($(findstring Darwin,$(UNAME)),Darwin)
OS:=Darwin
endif

VIRTUALENV_DIR:=$(if $(GLOBAL_VIRTUALENV_DIR),$(GLOBAL_VIRTUALENV_DIR),$(DIRECTORY)/.venv)

ifeq (Windows,$(OS))
VIRTUALENV_BIN:=$(VIRTUALENV_DIR)/Scripts
endif
ifeq ($(OS), $(filter $(OS),Linux Darwin))
VIRTUALENV_BIN:=$(VIRTUALENV_DIR)/bin
endif

REQUIREMENTS:=$(LIBS_DIRECTORY)/../requirements.txt

ACTIVATE:=$(VIRTUALENV_BIN)/activate
PIP:=$(VIRTUALENV_BIN)/pip
PYTHON:=$(VIRTUALENV_BIN)/python
ANSIBLE:=$(VIRTUALENV_BIN)/ansible
ANSIBLE_CFG:=$(DIRECTORY)/ansible.cfg
ANSIBLE_PLAYBOOK:=$(VIRTUALENV_BIN)/ansible-playbook

WORKSPACE:=$(if $(GLOBAL_WORKSPACE),$(GLOBAL_WORKSPACE),$(CURDIR)/.workspace)

WORKSPACE_BUILD:=$(WORKSPACE)/$(if $(WORKSPACE_NAME),$(WORKSPACE_NAME),default)
VERSION_FILE:=$(WORKSPACE)/version

VENV_LOCK:=$(WORKSPACE)/.venv

USER:=$(shell id -un)
USER_ID:=$(shell id -u)

GROUP:=$(shell id -gn)
GROUP_ID:=$(shell id -g)

UNAME:=$(shell uname)
ifeq ($(UNAME), Linux)
OS:=Linux
endif

ifeq ($(OS),)
OS:=Unknown
endif

### Build definitions
DEFAULT_NAME:=$(if $(NAME),$(NAME),$(if $(WORKSPACE_NAME),$(WORKSPACE_NAME),default))
DEFAULT_VERSION_MAJOR:=$(if $(VERSION_MAJOR),$(VERSION_MAJOR),1)
DEFAULT_VERSION_MINOR:=$(if $(VERSION_MINOR),$(VERSION_MINOR),0)
DEFAULT_VERSION_NO:=$(if $(VERSION_NO),$(VERSION_NO),0)
DEFAULT_VERSION_SUFFIX:=$(if $(VERSION_SUFFIX),$(VERSION_SUFFIX),ent)

ifeq ("$(VERSION_ID)", "")
ifneq ("$(wildcard $(VERSION_FILE))","")
VERSION_ID:=$(shell cat $(VERSION_FILE))
else
VERSION_ID:=$(shell TZ=UTC date '+%Y%m%d%H%M%S')
endif
endif

ifneq ($(VERSION_ID),"")
$(shell echo $(VERSION_ID) > $(VERSION_FILE))
endif

DEFAULT_VERSION_ID:=$(VERSION_ID)

VERSION:=$(DEFAULT_VERSION_MAJOR).$(DEFAULT_VERSION_MINOR).$(DEFAULT_VERSION_NO)-$(DEFAULT_VERSION_SUFFIX)-$(DEFAULT_VERSION_ID)

BUILD_DIR:=$(WORKSPACE_BUILD)/$(VERSION)/$(DEFAULT_NAME)

ANSIBLE_PLAYBOOK_RUN=. $(ACTIVATE); ANSIBLE_CONFIG=$(ANSIBLE_CFG) $(ANSIBLE_PLAYBOOK) \
                       -i $(LIBS_DIRECTORY)/inventory --force-handlers -e default_ansible_python_interpreter=$(PYTHON) \
                       -e VERSION_NO=$(DEFAULT_VERSION_NO) -e VERSION_MINOR=$(DEFAULT_VERSION_MINOR) \
                       -e VERSION_MAJOR=$(DEFAULT_VERSION_MAJOR) -e VERSION_ID=$(DEFAULT_VERSION_ID) \
                       -e VERSION_SUFFIX=$(DEFAULT_VERSION_SUFFIX) \
                       -e version=$(VERSION) -e user="$(USER)" -e user_id=$(USER_ID) -e build_dir=$(BUILD_DIR) \
                       -e group="$(GROUP)" -e group_id=$(GROUP_ID) -e build_name=$(DEFAULT_NAME) -e NAUTA_COMMIT=$(NAUTA_COMMIT) \
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

ifneq ($(OS), $(filter $(OS),Linux))
$(VIRTUALENV_DIR):
	@virtualenv -p python3.6 $(VIRTUALENV_DIR)

$(ACTIVATE): $(VIRTUALENV_DIR) $(REQUIREMENTS)
	@$(PIP) install --upgrade-strategy only-if-needed -r $(REQUIREMENTS)
	@touch $(ACTIVATE)
else
$(VIRTUALENV_DIR): $(VENV_LOCK)
	@flock $(VENV_LOCK) bash -c "if [ ! -d $(VIRTUALENV_DIR) ]; then virtualenv -p python3 $(VIRTUALENV_DIR); fi"

$(ACTIVATE): $(VIRTUALENV_DIR) $(REQUIREMENTS)
	@flock $(VENV_LOCK) bash -c "if [ ! -f $(VIRTUALENV_DIR)/.act-$(VERSION) ]; then $(PIP) install --upgrade-strategy only-if-needed -r $(REQUIREMENTS) && touch $(VIRTUALENV_DIR)/.act-$(VERSION); fi"
	@touch $(ACTIVATE)
endif

ENV_%:
	@ if [ "${ENV_${*}}" = "" ]; then \
		echo "Environment variable ENV_$* is not set, please set one before run"; \
		exit 1; \
	fi
