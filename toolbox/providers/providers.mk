UNAME := $(shell uname)
OS := Linux

ifeq ($(findstring Darwin,$(UNAME)),Darwin)
	OS := Darwin
endif

WORKSPACE := $(CURDIR)/.workspace
BIN := $(CURDIR)/.bin

$(WORKSPACE):
	@mkdir -p $(WORKSPACE)
	@touch $(WORKSPACE)

$(BIN):
	@mkdir -p $(BIN)
	@touch $(BIN)

TERRAFORM_DOWNLOAD_URL := https://releases.hashicorp.com/terraform/0.11.11/terraform_0.11.11_linux_amd64.zip

ifeq (Darwin,$(OS))
	TERRAFORM_DOWNLOAD_URL := https://releases.hashicorp.com/terraform/0.11.7/terraform_0.11.7_darwin_amd64.zip
endif

TERRAFORM := $(BIN)/terraform

$(TERRAFORM): $(BIN)
	@curl --silent --location $(TERRAFORM_DOWNLOAD_URL) -o $(TERRAFORM).zip
	cd $(BIN) && unzip $(TERRAFORM).zip
	@chmod +x $(TERRAFORM)
	@touch $(TERRAFORM)


include toolbox/providers/gcp/gcp.mk
