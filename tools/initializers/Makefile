PLATFORM_BUILD_DEPS = python3 pip virtualenv tar pigz docker

check-platform-dependencies:
LOOP := $(foreach exec,$(PLATFORM_BUILD_DEPS),$(if $(shell which $(exec)),exec,$(error "$(exec) seems to be not installed")))
