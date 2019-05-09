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

build-conditional-deep-clean:
ifeq (Darwin,$(OS))
	@echo Removes all virtualenv on MacOS
	@rm -rf $(VIRTUALENV_DIR)
	@rm -rf vendor
endif

build: $(ACTIVATE) set-version metrics-lib
ifeq (Windows,$(OS))
	. $(ACTIVATE); pip install pyinstaller==3.4
	rm -rf dist/

	git config --system core.longpaths true
	# build nctl
	. $(ACTIVATE); pyinstaller main.py --add-data "util/nbformat.v4.schema.json:.\nbformat\v4" -F --exclude-module readline -n nctl --hidden-import ruamel.yaml.jinja2.__plug_in__

	mkdir -vp dist/config/packs

	cp -Rf workflows dist/config
	cp zoo-repository.config dist/config/

	$(call clone_packs, $(shell git rev-parse --abbrev-ref HEAD))

	cp zoo-repository.config dist/config/

	# download and prepare Helm
	curl -o helm-v2.11.0-windows-amd64.zip https://storage.googleapis.com/kubernetes-helm/helm-v2.11.0-windows-amd64.zip

	rm -rf helm_tmp
	mkdir -vp helm_tmp

	7z x helm-v2.11.0-windows-amd64.zip -ohelm_tmp
	mv helm_tmp/windows-amd64/* helm_tmp
	rm -rf helm_tmp/windows-amd64

	mv helm_tmp/helm.exe dist/config

	mv helm_tmp/LICENSE dist/config/LICENSE_helm
	rm -f helm-v2.11.0-windows-amd64.zip
	rm -rf helm_tmp

endif
ifeq (Linux,$(OS))
	. $(ACTIVATE); pip install --upgrade pip==19.0.3
	. $(ACTIVATE); pip install pyinstaller==3.4
	rm -rf dist/

	. $(ACTIVATE); pyinstaller main.py --add-data util/nbformat.v4.schema.json:./nbformat/v4 --exclude-module readline -F -n nctl --hidden-import ruamel.yaml.jinja2.__plug_in__

	cp set-autocomplete-linux.sh dist/set-autocomplete.sh
	chmod +x dist/set-autocomplete.sh

	mkdir -vp dist/config/packs
	cp zoo-repository.config dist/config

	cp -Rf workflows dist/config

	$(call clone_packs, $(shell git rev-parse --abbrev-ref HEAD))

	curl -o helm-v2.11.0-linux-amd64.tar.gz https://storage.googleapis.com/kubernetes-helm/helm-v2.11.0-linux-amd64.tar.gz
	rm -rf helm_tmp
	mkdir -vp helm_tmp
	cd helm_tmp
	tar --strip-components=1 -xvf helm-v2.11.0-linux-amd64.tar.gz -C helm_tmp/
	mv helm_tmp/helm dist/config
	mv helm_tmp/LICENSE dist/config/LICENSE_helm
	rm -f helm-v2.11.0-linux-amd64.tar.gz
	rm -rf helm_tmp
endif
ifeq (Darwin,$(OS))
	. $(ACTIVATE); pip install --upgrade pip==19.0.3
	. $(ACTIVATE); pip install pyinstaller==3.4

	rm -rf dist/
	@. $(ACTIVATE); pyinstaller main.py --add-data util/nbformat.v4.schema.json:./nbformat/v4 --exclude-module readline -F -n nctl --hidden-import ruamel.yaml.jinja2.__plug_in__

	cp set-autocomplete-macos.sh dist/set-autocomplete.sh
	chmod +x dist/set-autocomplete.sh

	mkdir -vp dist/config/packs
	cp zoo-repository.config dist/config

	$(call clone_packs, $(shell git rev-parse --abbrev-ref HEAD))

	curl -o helm-v2.11.0-darwin-amd64.tar.gz https://storage.googleapis.com/kubernetes-helm/helm-v2.11.0-darwin-amd64.tar.gz
	rm -rf helm_tmp
	mkdir -vp helm_tmp
	cd helm_tmp
	tar --strip-components=1 -xvf helm-v2.11.0-darwin-amd64.tar.gz -C helm_tmp/
	mv helm_tmp/helm dist/config
	mv helm_tmp/LICENSE dist/config/LICENSE_helm
	rm -f helm-v2.11.0-darwin-amd64.tar.gz
	rm -rf helm_tmp

endif


	cp -Rf ../../nauta-user dist/config/
	mkdir -p dist/lib/
	mv experiment_metrics/dist/experiment_metrics-0.0.1.tar.gz dist/lib/
	cp -f license.txt dist/
	cp -Rf ../../docs/user-guide dist/docs
	mkdir -p dist/examples/
	cp -Rf example-python/package_examples/* dist/examples/
	cp node_config dist/config/

ifneq (,$(SCM_REPOSITORY_STATE))
	mkdir dist/config/scm/
	echo "$(SCM_REPOSITORY_STATE)" > dist/config/scm/sha_sum.json
endif

metrics-lib:
	@. $(ACTIVATE); cd experiment_metrics && python setup.py sdist

style: $(DEV_VIRTUALENV_MARK)
	@. $(ACTIVATE); flake8 draft/ util/ commands/ main.py

test: $(DEV_VIRTUALENV_MARK)
	@. $(ACTIVATE); LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 py.test

cli-check: venv-dev test style

test-with-code-cov: $(DEV_VIRTUALENV_MARK)
	#@. $(ACTIVATE); LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 py.test
	@. $(ACTIVATE); LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 py.test --cov=. --cov-config tox.ini --cov-report term-missing

VERSION_CLIENT_MAJOR ?= 1
VERSION_CLIENT_MINOR ?= 0
VERSION_CLIENT_NO ?= 0
VERSION_SUFFIX ?= oss

BUILD_ID ?= dev

export CLI_ARTIFACT_DIRECTORY:=$(CURDIR)
export CLI_ARTIFACT_VERSION_STRING:=$(VERSION_CLIENT_MAJOR).$(VERSION_CLIENT_MINOR).$(VERSION_CLIENT_NO)-$(VERSION_SUFFIX)-$(BUILD_ID)

ifeq (Windows,$(OS))
export CLI_ARTIFACT_NAME:=nctl-$(CLI_ARTIFACT_VERSION_STRING)-windows.zip
export CLI_ARTIFACT_PLATFORM:=windows
endif
ifeq (Linux,$(OS))
export CLI_ARTIFACT_NAME:=nctl-$(CLI_ARTIFACT_VERSION_STRING)-linux.tar.gz
export CLI_ARTIFACT_PLATFORM:=linux
endif
ifeq (Darwin,$(OS))
export CLI_ARTIFACT_NAME:=nctl-$(CLI_ARTIFACT_VERSION_STRING)-darwin.tar.gz
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
ifneq ($(ENV_OUTPUT_ARTIFACT_DIRECTORY),)
	mkdir -p $(ENV_OUTPUT_ARTIFACT_DIRECTORY)/nctl
	cp -r $(CLI_ARTIFACT_DIRECTORY)/$(CLI_ARTIFACT_NAME) $(ENV_OUTPUT_ARTIFACT_DIRECTORY)/nctl

ifeq (True,$(ENV_CALCULATESUM))
	@echo Calculate file control sum and upload to the releases directory
ifeq (Linux,$(OS))
	sha256sum "$(CLI_ARTIFACT_DIRECTORY)/$(CLI_ARTIFACT_NAME)" > "$(CLI_ARTIFACT_DIRECTORY)/$(CLI_ARTIFACT_NAME).sha256sum"
endif
ifeq (Darwin,$(OS))
	shasum -a 256 "$(CLI_ARTIFACT_DIRECTORY)/$(CLI_ARTIFACT_NAME)" > "$(CLI_ARTIFACT_DIRECTORY)/$(CLI_ARTIFACT_NAME).sha256sum"
endif
ifeq (Windows,$(OS))
	powershell -Command "& { Get-FileHash -Algorithm SHA256 -Path $(CLI_ARTIFACT_DIRECTORY)/$(CLI_ARTIFACT_NAME) > $(CLI_ARTIFACT_DIRECTORY)/$(CLI_ARTIFACT_NAME).sha256sum }"
endif
	cp -r $(CLI_ARTIFACT_DIRECTORY)/$(CLI_ARTIFACT_NAME).sha256sum $(ENV_OUTPUT_ARTIFACT_DIRECTORY)/nctl/$(CLI_ARTIFACT_NAME).sha256sum
endif
endif

set-version:
	./set-version.sh "$(VERSION_CLIENT_MAJOR).$(VERSION_CLIENT_MINOR).$(VERSION_CLIENT_NO)-$(VERSION_SUFFIX)-$(BUILD_ID)"

define clone_packs
	# populate draft/packs with nauta-zoo repo
	cd dist/config/packs && git clone https://github.com/IntelAI/nauta-zoo.git && cd nauta-zoo && git checkout $(1) 2> /dev/null || true
	cd dist/config/packs/nauta-zoo && echo "Using packs from nauta-zoo repository with branch:" && git rev-parse --abbrev-ref HEAD
	mv dist/config/packs/nauta-zoo/* dist/config/packs/
	rm -rf dist/config/packs/nauta-zoo
endef
