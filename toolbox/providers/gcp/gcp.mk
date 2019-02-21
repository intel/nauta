
gcp-create: $(ACTIVATE) $(TERRAFORM) ENV_NAME $(VAULT) $(WORKSPACE) ENV_EXTERNAL_PUBLIC_KEY ENV_EXTERNAL_KEY ENV_CLUSTER_CONFIG_FILE ENV_NETWORK_SETTINGS ENV_SERVICE_ACCOUNT_CONFIG
	@. $(ACTIVATE); ANSIBLE_CONFIG=$(CURDIR)/toolbox/providers/gcp/ansible.cfg $(ANSIBLE_PLAYBOOK) -i $(CURDIR)/toolbox/providers/inventory \
	 $(CURDIR)/toolbox/providers/gcp/gcp.yml \
	-e s3_url=$(ENV_S3_URL) \
	-e s3_secret_key=$(ENV_SECRET_KEY) \
	-e s3_access_key=$(ENV_ACCESS_KEY) \
	-e prefix=$(ENV_NAME) \
	-e local_python_interpreter=$(PYTHON) \
	-e workspace=$(WORKSPACE) \
	-e terraform=$(TERRAFORM) \
	-e @$(ENV_NETWORK_SETTINGS) \
	-e service_account_config_file=$(ENV_SERVICE_ACCOUNT_CONFIG) \
	-e external_key=$(ENV_EXTERNAL_KEY) \
	-e external_public_key=$(ENV_EXTERNAL_PUBLIC_KEY) \
	-e cluster_config_file=$(ENV_CLUSTER_CONFIG_FILE) \
	$(if $(TF_VAR_POOL_SIZE), -e tf_pool_size=$(TF_VAR_POOL_SIZE),) \
	$(if $(TF_VAR_POOL_TYPE), -e tf_pool_type=$(TF_VAR_POOL_TYPE),) \
	-e output_file=$(if $(K8S_OUTPUT_FILE),$(K8S_OUTPUT_FILE),empty)

gcp-destroy: $(ACTIVATE) $(WORKSPACE) $(TERRAFORM) ENV_NAME ENV_NETWORK_SETTINGS ENV_CLUSTER_CONFIG_FILE ENV_SERVICE_ACCOUNT_CONFIG
	@. $(ACTIVATE); ANSIBLE_CONFIG=$(CURDIR)/toolbox/providers/gcp/ansible.cfg $(ANSIBLE_PLAYBOOK) -i $(CURDIR)/toolbox/providers/inventory \
	 $(CURDIR)/toolbox/providers/gcp/gcp-clean.yml \
	-e s3_url=$(ENV_S3_URL) \
	-e s3_secret_key=$(ENV_SECRET_KEY) \
	-e s3_access_key=$(ENV_ACCESS_KEY) \
	-e prefix=$(ENV_NAME) \
	-e local_python_interpreter=$(PYTHON) \
	-e workspace=$(WORKSPACE) \
	-e terraform=$(TERRAFORM) \
	-e cluster_config_file=$(ENV_CLUSTER_CONFIG_FILE) \
	$(if $(TF_VAR_POOL_SIZE), -e tf_pool_size=$(TF_VAR_POOL_SIZE),) \
	$(if $(TF_VAR_POOL_TYPE), -e tf_pool_type=$(TF_VAR_POOL_TYPE),) \
	-e @$(ENV_NETWORK_SETTINGS) \
	-e service_account_config_file=$(ENV_SERVICE_ACCOUNT_CONFIG) \
	--vault-password-file=$(VAULT) \
	-e external_key=$(ENV_EXTERNAL_KEY) \
	-e external_public_key=$(ENV_EXTERNAL_PUBLIC_KEY)

gcp-recreate: gcp-destroy gcp-create

gcp-nauta-install: $(ACTIVATE) ENV_NAME ENV_S3_URL ENV_SECRET_KEY ENV_ACCESS_KEY
	@$(K8S_BM_DEPLOYMENT_HOME)/files/gcp_install.sh \
	    --k8s-clustername $(ENV_NAME) \
	    --k8s-use-latest-if-install-not-found true \
	    --k8s-image-version $(K8S_IMAGE_VERSION) \
	    --k8s-gateway-address $(K8S_GATEWAY_ADDRESS) \
	    --k8s-gateway-key $(ENV_EXTERNAL_KEY)

gcp-clean:
	@echo ===== Removing workspace directory $(WORKSPACE) =====
	@rm -rf $(WORKSPACE)
