include $(CURDIR)/libs/global.mk

USER:=$(shell id -un)
USER_ID:=$(shell id -u)

ANSIBLE_CFG:=$(CURDIR)/ansible.cfg

ANSIBLE_PLAYBOOK_RUN=ANSIBLE_CONFIG=$(ANSIBLE_CFG) $(ANSIBLE_PLAYBOOK) \
                       -i $(ENV_INVENTORY) $(if $(ENV_CONFIG),-e @$(ENV_CONFIG) ,) \
                       $(PLAYBOOK)

configured: ENV_INVENTORY

platform-install: PLAYBOOK=$(CURDIR)/platform/dls.yml
platform-install: configured $(ANSIBLE_PLAYBOOK)
	@$(ANSIBLE_PLAYBOOK_RUN) --tags init,install

dls4e-init: PLAYBOOK=$(CURDIR)/dls4e/init.yml
dls4e-init: configured $(ANSIBLE_PLAYBOOK)
	@$(ANSIBLE_PLAYBOOK_RUN)

dls4e-install: PLAYBOOK=$(CURDIR)/dls4e/install.yml
dls4e-install: configured $(ANSIBLE_PLAYBOOK)
	@$(ANSIBLE_PLAYBOOK_RUN) -e upgrade=False

dls4e-upgrade: PLAYBOOK=$(CURDIR)/dls4e/install.yml
dls4e-upgrade: configured $(ANSIBLE_PLAYBOOK)
	@$(ANSIBLE_PLAYBOOK_RUN) -e upgrade=True

install: platform-install dls4e-install
