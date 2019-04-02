VIRTUALENV_DIR := .venv
ACTIVATE := $(VIRTUALENV_DIR)/bin/activate

clean:
	@rm -rf __pycache__ .cache $(VIRTUALENV_DIR)

venv: $(ACTIVATE)
$(ACTIVATE): requirements.txt
	@python3.6 -m venv $(VIRTUALENV_DIR)
	@chmod +x $(ACTIVATE)
	@. $(ACTIVATE); python -m pip install -U pip
	@. $(ACTIVATE); pip install -r requirements.txt;
