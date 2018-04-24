
.PHONY: yum-build

yum-build: PLAYBOOK=$(CURDIR)/yum.yml
yum-build: $(ACTIVATE) $(BUILD_DIR) $(TMP_DIR)
	@$(ANSIBLE_PLAYBOOK_RUN)
