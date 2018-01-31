VIRTUALENV_DIR = $(CURDIR)/.venv
ACTIVATE := $(VIRTUALENV_DIR)/bin/activate

TOOLBOX_HOME=$(CURDIR)/toolbox

USER := $(shell id -un)
USER_ID := $(shell id -u)

venv: $(ACTIVATE)
$(ACTIVATE): requirements.txt
	@virtualenv -p python3.6 $(VIRTUALENV_DIR)
	@chmod +x $(ACTIVATE)
	@. $(ACTIVATE); pip install --upgrade-strategy only-if-needed -r requirements.txt;

include toolbox/checks/checks.mk

venv-clean:
	@rm -rf $(CURDIR)/.venv
