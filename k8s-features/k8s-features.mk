K8S_FEATURES_HOME = $(CURDIR)/k8s-features

k8s-features-install: venv K8S_FEATURES_LIST
	$(eval K8S_CONFIG_LOCATION := $(if $(K8S_CONFIG_LOCATION), $(K8S_CONFIG_LOCATION),~/.kube/config))
	@echo "======================= k8s-features-install: effective kube config: $(K8S_CONFIG_LOCATION) ======================="
	@. $(ACTIVATE); ansible-playbook -e @./config.yml $(K8S_FEATURES_HOME)/dls.kubernetes.feature.yml \
	    -e kube_config=$(K8S_CONFIG_LOCATION) \
	    -e k8s_features=$(K8S_FEATURES_LIST) \
	    -e k8s_operation=install


k8s-features-uninstall: venv K8S_FEATURES_LIST
	$(eval K8S_CONFIG_LOCATION := $(if $(K8S_CONFIG_LOCATION), $(K8S_CONFIG_LOCATION),~/.kube/config))
	@echo "======================= k8s-features-install: effective kube config: $(K8S_CONFIG_LOCATION) ======================="
	@. $(ACTIVATE); ansible-playbook -e @./config.yml $(K8S_FEATURES_HOME)/dls.kubernetes.feature.yml \
	    -e kube_config=$(K8S_CONFIG_LOCATION) \
	    -e k8s_features=$(K8S_FEATURES_LIST) \
	    -e k8s_operation=uninstall
