PLATFORM_BUILD_DEPS = python3 virtualenv tar pigz docker git

check-platform-dependencies:
LOOP := $(foreach exec,$(PLATFORM_BUILD_DEPS),$(if $(shell which $(exec)),$(info $(exec) dependency installed),$(error $(exec) seems to be not installed)))
