
create-gateway-users: $(ACTIVATE) $(WORKSPACE) $(ENV_GATEWAY_USERS)
	@. $(ACTIVATE); ANSIBLE_CONFIG=$(CURDIR)/toolbox/support/gateway-users/ansible.cfg $(ANSIBLE_PLAYBOOK) -i $(CURDIR)/toolbox/support/gateway-users/inventory \
	 $(CURDIR)/toolbox/support/gateway-users/gateway-workers.yml \
	-e gateway_users_config_file=$(ENV_GATEWAY_USERS) \
	-e pool_type=$(ENV_POOL_TYPE) \
	-e local_python_interpreter=$(PYTHON) \
	-e $(CURDIR)/toolbox/support/gateway-users/group_vars/all/admin-user.yml \
	-e workspace=$(WORKSPACE)
