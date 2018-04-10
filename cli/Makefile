# Copyright (c) 2018, Intel Corporation

# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

VIRTUALENV_DIR := .venv
DEV_VIRTUALENV_MARK := $(VIRTUALENV_DIR)/dev
ACTIVATE := $(VIRTUALENV_DIR)/bin/activate

clean:
	@rm -rf $(VIRTUALENV_DIR) __pycache__ .cache build dist *.spec charts Dockerfile .draftignore *.toml .pytest_cache

venv: $(ACTIVATE)
$(ACTIVATE): requirements.txt
	@python3.6 -m venv $(VIRTUALENV_DIR)
	@chmod +x $(ACTIVATE)
	@. $(ACTIVATE); pip install -r requirements.txt;

venv-dev: $(DEV_VIRTUALENV_MARK)
$(DEV_VIRTUALENV_MARK): requirements-dev.txt $(ACTIVATE)
	@touch $(DEV_VIRTUALENV_MARK)
	@. $(ACTIVATE); pip install -r requirements-dev.txt;

include cli.mk
