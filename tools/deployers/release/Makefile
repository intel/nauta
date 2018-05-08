include $(CURDIR)/libs/global.mk

USER:=$(shell id -un)
USER_ID:=$(shell id -u)

ANSIBLE_CFG:=$(CURDIR)/ansible.cfg

ANSIBLE_PLAYBOOK_RUN=ANSIBLE_CONFIG=$(ANSIBLE_CFG) $(ANSIBLE_PLAYBOOK) \
                       -i $(ENV_INVENTORY) $(if $(ENV_CONFIG),-e @$(ENV_CONFIG) ,) \
                       $(PLAYBOOK)

configured: ENV_INVENTORY

install: PLAYBOOK=$(CURDIR)/platform/dls.yml
install: configured $(ANSIBLE_PLAYBOOK)
	@$(ANSIBLE_PLAYBOOK_RUN) --tags init,install
