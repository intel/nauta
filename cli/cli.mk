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


build: $(ACTIVATE) set-version
	@. $(ACTIVATE); pip install pyinstaller;

ifeq (Windows,$(OS))
	@. $(ACTIVATE); pyinstaller --paths "C:\Program Files (x86)\Windows Kits\10\Redist\ucrt\DLLs\x64" -F main.py -n dlsctl;
	@curl http://repository.toolbox.nervana.sclab.intel.com/files/draft-bundles/windows/draft-v0.13.0-windows-amd64.7z -o draft.7z
	@mkdir dist/dls_ctl_config/
	@7z x draft.7z -odist/dls_ctl_config/
	@rm -f draft.7z
endif
ifeq (Linux,$(OS))
	@. $(ACTIVATE); pyinstaller -F main.py -n dlsctl;
	@curl http://repository.toolbox.nervana.sclab.intel.com/files/draft-bundles/linux/draft-v0.13.0-linux-amd64.tar.gz -o draft.tar.gz
	@mkdir dist/dls_ctl_config/
	@tar -zxf draft.tar.gz -C dist/dls_ctl_config/
	@rm -f draft.tar.gz
endif
ifeq (Darwin,$(OS))
	@. $(ACTIVATE); pyinstaller -F main.py -n dlsctl;
	@curl http://repository.toolbox.nervana.sclab.intel.com/files/draft-bundles/mac/draft-v0.13.0-darwin-amd64.tar.gz -o draft.tar.gz
	@mkdir dist/dls_ctl_config/
	@tar -zxf draft.tar.gz -C dist/dls_ctl_config/
	@rm -f draft.tar.gz
endif

	@cp -Rf draft/packs/* dist/dls_ctl_config/.draft/packs/
	@cp -Rf ../dls4e-user dist/dls_ctl_config/

style: $(DEV_VIRTUALENV_MARK)
	@. $(ACTIVATE); flake8 draft/ util/ commands/ main.py

test: $(DEV_VIRTUALENV_MARK)
	@. $(ACTIVATE); LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 py.test

cli-check: venv-dev test style


export CLI_ARTIFACT_DIRECTORY:=$(CURDIR)
export CLI_ARTIFACT_VERSION_STRING:=$(VERSION_CLIENT_MAJOR).$(VERSION_CLIENT_MINOR).$(VERSION_CLIENT_NO)-$(BUILD_ID)

ifeq (Windows,$(OS))
export CLI_ARTIFACT_NAME:=dlsctl-$(CLI_ARTIFACT_VERSION_STRING)-windows.zip
export CLI_ARTIFACT_PLATFORM:=windows
endif
ifeq (Linux,$(OS))
export CLI_ARTIFACT_NAME:=dlsctl-$(CLI_ARTIFACT_VERSION_STRING)-linux.tar.gz
export CLI_ARTIFACT_PLATFORM:=linux
endif
ifeq (Darwin,$(OS))
export CLI_ARTIFACT_NAME:=dlsctl-$(CLI_ARTIFACT_VERSION_STRING)-darwin.tar.gz
export CLI_ARTIFACT_PLATFORM:=darwin
endif

pack: build
ifeq (Windows,$(OS))
	@7z a -tzip $(CLI_ARTIFACT_NAME) ./dist/*
endif
ifeq (Linux,$(OS))
	@tar -zcf $(CLI_ARTIFACT_NAME) -C dist .
endif
ifeq (Darwin,$(OS))
	@tar -zcf $(CLI_ARTIFACT_NAME) -C dist .
endif

push: pack
ifneq (Windows,$(OS))
	@cd $(CURDIR)/.. && make tools-push ENV_SRC=$(CLI_ARTIFACT_DIRECTORY)/$(CLI_ARTIFACT_NAME) ENV_DEST=releases/dlsctl/$(CLI_ARTIFACT_PLATFORM)/$(CLI_ARTIFACT_NAME)
else
	@echo aws --endpoint-url $(ENV_S3_URL) s3 cp "$(CLI_ARTIFACT_DIRECTORY)/$(CLI_ARTIFACT_NAME)" "s3://repository/releases/dlsctl/$(CLI_ARTIFACT_PLATFORM)/$(CLI_ARTIFACT_NAME)"
	@aws --endpoint-url $(ENV_S3_URL) s3 cp "$(CLI_ARTIFACT_DIRECTORY)/$(CLI_ARTIFACT_NAME)" "s3://repository/releases/dlsctl/$(CLI_ARTIFACT_PLATFORM)/$(CLI_ARTIFACT_NAME)"
endif

VERSION_CLIENT_MAJOR ?= 1
VERSION_CLIENT_MINOR ?= 0
VERSION_CLIENT_NO ?= 0
BUILD_ID ?= develop
VERSION_CLIENT_BUMP_PART ?= patch

set-version:
	./set-version.sh "$(VERSION_CLIENT_MAJOR).$(VERSION_CLIENT_MINOR).$(VERSION_CLIENT_NO)-$(BUILD_ID)"
