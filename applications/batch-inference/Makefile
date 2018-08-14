VIRTUALENV_DIR := .venv
DEV_VIRTUALENV_MARK := $(VIRTUALENV_DIR)/dev

ACTIVATE := $(VIRTUALENV_DIR)/bin/activate

clean:
	@rm -rf __pycache__ $(VIRTUALENV_DIR) .pytest_cache app/tests/.pytest_cache .coverage

venv: $(ACTIVATE)
$(ACTIVATE): requirements.txt
	@python3.6 -m venv $(VIRTUALENV_DIR)
	@chmod +x $(ACTIVATE)
	@. $(ACTIVATE); python -m pip install -U pip
	@. $(ACTIVATE); pip install -r requirements.txt;

venv-dev: $(DEV_VIRTUALENV_MARK)
$(DEV_VIRTUALENV_MARK): requirements-dev.txt $(ACTIVATE)
	@touch $(DEV_VIRTUALENV_MARK)
	@. $(ACTIVATE); pip install -r requirements-dev.txt;

style: $(DEV_VIRTUALENV_MARK)
	@. $(ACTIVATE); flake8 .

test: $(DEV_VIRTUALENV_MARK)
	@. $(ACTIVATE); py.test --cov-report term-missing --cov-config tox.ini --cov=app .
