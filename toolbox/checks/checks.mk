ansible-syntax-check: $(ACTIVATE)
#	===============================================================================
#	                Please add ansible playbooks here"
#	===============================================================================
	@echo skipped


code-yamllint: $(ACTIVATE)
	@. $(ACTIVATE); yamllint .

code-check-syntax:
	@$(MAKE) ansible-syntax-check
	@$(MAKE) code-yamllint

code-check-license:
	mvn -f toolbox/checks/license_check.xml license:check -Dorg.slf4j.simpleLogger.defaultLogLevel=warning

code-check-all: code-check-license code-check-syntax
