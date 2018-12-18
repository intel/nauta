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
	. $(ACTIVATE); pip install pyinstaller
	rm -rf dist/
ifeq (Windows,$(OS))

	git config --system core.longpaths true
	# build dlsctl
	. $(ACTIVATE); pyinstaller --paths "C:\Program Files (x86)\Windows Kits\10\Redist\ucrt\DLLs\x64" main.py --add-data "util/nbformat.v4.schema.json:.\nbformat\v4" -F --exclude-module readline -n dlsctl


	# download and prepare Draft
	curl https://azuredraft.blob.core.windows.net/draft/draft-v0.14.1-windows-amd64.zip -o draft.zip
	mkdir dist/config/
	7z x draft.zip -odist/config/
	rm -f draft.zip
	mv dist/config/windows-amd64/* dist/config
	rm -rf dist/config/windows-amd64

	dist\config\draft init --home dist/config/.draft
	rm -rf dist/config/.draft/packs/*
	rm -rf dist/config/.draft/plugins/
	mkdir -p dist/config/.draft/packs/https-github.com-Azure-draft/packs
	cp -Rf draft/packs/* dist/config/.draft/packs/https-github.com-Azure-draft/packs/
	cd dist/config && ln -s .draft/packs/https-github.com-Azure-draft/packs packs

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


	# download and prepare Socat
	docker pull alpine/socat:1.0.3
	docker tag alpine/socat:1.0.3 socat-container-image:1.0.3
	docker save socat-container-image:1.0.3 > dist/config/socat-container-image.tar
	gzip dist/config/socat-container-image.tar
	docker rmi alpine/socat:1.0.3
endif
ifeq (Linux,$(OS))
	. $(ACTIVATE); pyinstaller main.py --add-data util/nbformat.v4.schema.json:./nbformat/v4 --exclude-module readline -F -n dlsctl
	curl https://azuredraft.blob.core.windows.net/draft/draft-v0.14.1-linux-amd64.tar.gz -o draft.tar.gz
	cp set-autocomplete-linux.sh dist/set-autocomplete.sh
	chmod +x dist/set-autocomplete.sh
	mkdir -vp dist/config/
	tar -zxf draft.tar.gz -C dist/config/
	rm -f draft.tar.gz
	mv dist/config/linux-amd64/* dist/config
	rm -rf dist/config/linux-amd64
	PATH=$$PATH:`pwd`/dist/config draft init --home dist/config/.draft
	rm -rf dist/config/.draft/packs/*
	rm -rf dist/config/.draft/plugins/
	mkdir -p dist/config/.draft/packs/https-github.com-Azure-draft/packs
	cp -Rf draft/packs/* dist/config/.draft/packs/https-github.com-Azure-draft/packs/
	cd dist/config && ln -s .draft/packs/https-github.com-Azure-draft/packs packs

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
	@. $(ACTIVATE); pyinstaller main.py --add-data util/nbformat.v4.schema.json:./nbformat/v4 --exclude-module readline -F -n dlsctl
	curl https://azuredraft.blob.core.windows.net/draft/draft-v0.14.1-darwin-amd64.tar.gz -o draft.tar.gz
	cp set-autocomplete-macos.sh dist/set-autocomplete.sh
	chmod +x dist/set-autocomplete.sh
	mkdir -vp dist/config/
	tar -zxf draft.tar.gz -C dist/config/
	rm -f draft.tar.gz
	mv dist/config/darwin-amd64/* dist/config
	rm -rf dist/config/darwin-amd64
	PATH=$$PATH:`pwd`/dist/config draft init --home dist/config/.draft
	rm -rf dist/config/.draft/packs/*
	rm -rf dist/config/.draft/plugins/
	mkdir -p dist/config/.draft/packs/https-github.com-Azure-draft/packs
	cp -Rf draft/packs/* dist/config/.draft/packs/https-github.com-Azure-draft/packs/
	cd dist/config && ln -s .draft/packs/https-github.com-Azure-draft/packs packs

	curl -o helm-v2.11.0-darwin-amd64.tar.gz https://storage.googleapis.com/kubernetes-helm/helm-v2.11.0-darwin-amd64.tar.gz
	rm -rf helm_tmp
	mkdir -vp helm_tmp
	cd helm_tmp
	tar --strip-components=1 -xvf helm-v2.11.0-darwin-amd64.tar.gz -C helm_tmp/
	mv helm_tmp/helm dist/config
	mv helm_tmp/LICENSE dist/config/LICENSE_helm
	rm -f helm-v2.11.0-darwin-amd64.tar.gz
	rm -rf helm_tmp

	# download and prepare Socat
	docker pull alpine/socat:1.0.3
	docker tag alpine/socat:1.0.3 socat-container-image:1.0.3
	docker save socat-container-image:1.0.3 > dist/config/socat-container-image.tar
	gzip dist/config/socat-container-image.tar
	docker rmi alpine/socat:1.0.3

endif


	cp -Rf ../../dls4e-user dist/config/
	mkdir -p dist/lib/
	mv experiment_metrics/dist/experiment_metrics-0.0.1.tar.gz dist/lib/
	cp -f license.txt dist/
	cp -Rf docs dist/docs
	mkdir -p dist/examples/
	cp -Rf example-python/package_examples/* dist/examples/

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
	@. $(ACTIVATE); LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 py.test
	#@. $(ACTIVATE); LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 py.test --cov=. --cov-config tox.ini --cov-report term-missing



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
	mkdir -p $(ENV_OUTPUT_ARTIFACT_DIRECTORY)/dlsctl
	cp -r $(CLI_ARTIFACT_DIRECTORY)/$(CLI_ARTIFACT_NAME) $(ENV_OUTPUT_ARTIFACT_DIRECTORY)/dlsctl

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
	cp -r $(CLI_ARTIFACT_DIRECTORY)/$(CLI_ARTIFACT_NAME).sha256sum $(ENV_OUTPUT_ARTIFACT_DIRECTORY)/dlsctl/$(CLI_ARTIFACT_NAME).sha256sum
endif


VERSION_CLIENT_MAJOR ?= 1
VERSION_CLIENT_MINOR ?= 0
VERSION_CLIENT_NO ?= 0
BUILD_ID ?= dev
VERSION_CLIENT_BUMP_PART ?= patch

set-version:
	./set-version.sh "$(VERSION_CLIENT_MAJOR).$(VERSION_CLIENT_MINOR).$(VERSION_CLIENT_NO)-$(BUILD_ID)"
