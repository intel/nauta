DIRECTORY:=$(CURDIR)
WORKSPACE_NAME:=rpms
include $(CURDIR)/../makelibs/commons.mk

configured: ENV_SRC ENV_DEST ENV_OUTPUT_ARTIFACT_DIRECTORY

build: configured $(ACTIVATE)
	mkdir -p $(ENV_OUTPUT_ARTIFACT_DIRECTORY)/dls4e/
	cp -r $(ENV_SRC) $(ENV_OUTPUT_ARTIFACT_DIRECTORY)/dls4e/
