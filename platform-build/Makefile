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

ANSIBLE_PLAYBOOK_RUN=. $(ACTIVATE); ANSIBLE_CONFIG=$(ANSIBLE_CFG) $(ANSIBLE_PLAYBOOK) -e @$(CONFIG) \
                      -e default_local_python_intepreter=$(PYTHON) -i $(if $(INVENTORY),$(INVENTORY),$(LOCAL_INVENTORY)) \
                      -e build=$(BUILD) -e VERSION_NO=$(DEFAULT_VERSION_NO) -e VERSION_MINOR=$(DEFAULT_VERSION_MINOR) \
                      -e VERSION_MAJOR=$(DEFAULT_VERSION_MAJOR) -e user=$(USER) -e user_id=$(USER_ID) \
                      -e build_dir=$(BUILD_DIR) -e workspace_dir=$(WORKSPACE_BUILD) -e build_id=$(DEFAULT_BUILD_ID) \
                       $(PLAYBOOK) -e tmp_dir=$(TMP_DIR)

TOOLBOX_HOME:=$(CURDIR)/toolbox

USER:=$(shell id -un)
USER_ID:=$(shell id -u)

.PHONY: venv clean

### Build definitions
DEFAULT_VERSION_MAJOR:=$(if $(VERSION_MAJOR),$(VERSION_MAJOR),1)
DEFAULT_VERSION_MINOR:=$(if $(VERSION_MINOR),$(VERSION_MINOR),0)
DEFAULT_VERSION_NO:=$(if $(VERSION_NO),$(VERSION_NO),0)
DEFAULT_BUILD_ID:=$(if $(BUILD_ID),$(BUILD_ID),$(shell TZ=UTC date '+%y%m%d%H%M%S'))
BUILD:=$(DEFAULT_VERSION_MAJOR).$(DEFAULT_VERSION_MINOR).$(DEFAULT_VERSION_NO)-$(DEFAULT_BUILD_ID)

### Workspace definitions
WORKSPACE:=$(CURDIR)/.workspace

WORKSPACE_BUILD:=$(WORKSPACE)/build

BUILD_DIR:=$(WORKSPACE_BUILD)/$(BUILD)

WORKSPACE_TMP:=$(WORKSPACE)/tmp

TMP_DIR:=$(WORKSPACE_TMP)/$(BUILD)

$(VIRTUALENV_DIR):
	@virtualenv -p python3.6 $(VIRTUALENV_DIR)

$(ACTIVATE): $(VIRTUALENV_DIR) $(REQUIREMENTS)
	@$(PIP) install --upgrade-strategy only-if-needed -r $(REQUIREMENTS)
	@touch $(ACTIVATE)

$(WORKSPACE):
	@mkdir -p $(WORKSPACE)
	@touch $(WORKSPACE)

$(WORKSPACE_BUILD): $(WORKSPACE)
	@mkdir -p $(WORKSPACE_BUILD)
	@touch $(WORKSPACE_BUILD)

$(BUILD_DIR): $(WORKSPACE_BUILD)
	@mkdir -p $(BUILD_DIR)
	@touch $(BUILD_DIR)
	@ln -fs $(BUILD_DIR)/ $(WORKSPACE)/build-latest

$(TMP_DIR): $(WORKSPACE)
	@mkdir -p $(TMP_DIR)
	@touch $(TMP_DIR)

venv: $(ACTIVATE)
clean: clean-venv clean-workspace

clean-venv:
	@rm -rf $(VENV)

clean-workspace:
	@rm -rf $(WORKSPACE)

include make/yum.mk
