ansible-syntax-check: $(ACTIVATE) .vault_pass.txt
#	===============================================================================
#	                Please add ansible playbooks here"
#	===============================================================================
#	@. $(ACTIVATE); ansible-playbook toolbox/scm/scm.yml -e @./toolbox/config.yml --vault-password-file ./.vault_pass.txt --syntax-check


yamllint: $(ACTIVATE)
	@. $(ACTIVATE); yamllint .

check-syntax:
	@$(MAKE) ansible-syntax-check
	@$(MAKE) yamllint

check-license:
	mvn -f toolbox/checks/license_check.xml license:check

check-all: check-license check-syntax

