include $(CURDIR)/libs/global.mk

USER:=$(shell id -un)
USER_ID:=$(shell id -u)

ANSIBLE_CFG:=$(CURDIR)/ansible.cfg

.PHONY: dls4e platform-install dls4e-install dls4e-upgrade

ANSIBLE_PLATFORM_PLAYBOOK_RUN=ANSIBLE_CONFIG=$(ANSIBLE_CFG) $(ANSIBLE_PLAYBOOK) \
                              -i $(ENV_INVENTORY) $(if $(ENV_CONFIG),-e @$(ENV_CONFIG) ,) \
                              -e local_config=$(LOCAL_CONFIG) -e local_kubeconfig=$(F_KUBECONFIG) \
                              $(PLAYBOOK)

ANSIBLE_DLS4E_PLAYBOOK_RUN=ANSIBLE_CONFIG=$(ANSIBLE_CFG) $(ANSIBLE_PLAYBOOK) \
							  $(if $(ENV_CONFIG),-e @$(ENV_CONFIG) ,) \
                              $(if $(ENV_INVENTORY),-i $(ENV_INVENTORY),-c local -i localhost,) \
                              $(PLAYBOOK) -e upgrade=$(UPGRADE) -e kubectl=$(KUBECTL) -e helm=$(HELM) \
                              -e kubeconfig=$(F_KUBECONFIG) -e loader=$(LOADER)


configured: ENV_INVENTORY

F_KUBECONFIG:=$(if $(ENV_KUBECONFIG),$(ENV_KUBECONFIG),~/.kube/config)

platform-install: PLAYBOOK=$(CURDIR)/platform/dls.yml
platform-install: configured $(ANSIBLE_PLAYBOOK)
	@$(ANSIBLE_PLATFORM_PLAYBOOK_RUN) --tags init,install

dls4e-install: UPGRADE=false
dls4e-install: dls4e

dls4e-upgrade: UPGRADE=true
dls4e-upgrade: dls4e
dls4e: PLAYBOOK=$(CURDIR)/dls4e/install.yml
dls4e: $(ANSIBLE_PLAYBOOK)
dls4e: $(KUBECTL)
dls4e: $(HELM)
dls4e: $(LOADER)
dls4e: PATH:=$(PATH):$(LIBS_DIRECTORY)/../bin/$(DLSE_OS)
dls4e:
	@$(ANSIBLE_DLS4E_PLAYBOOK_RUN)



install: platform-install dls4e-install
