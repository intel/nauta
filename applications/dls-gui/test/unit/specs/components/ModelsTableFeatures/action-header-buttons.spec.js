/**
 * INTEL CONFIDENTIAL
 * Copyright (c) 2018 Intel Corporation
 *
 * The source code contained or described herein and all documents related to
 * the source code ("Material") are owned by Intel Corporation or its suppliers
 * or licensors. Title to the Material remains with Intel Corporation or its
 * suppliers and licensors. The Material contains trade secrets and proprietary
 * and confidential information of Intel or its suppliers and licensors. The
 * Material is protected by worldwide copyright and trade secret laws and treaty
 * provisions. No part of the Material may be used, copied, reproduced, modified,
 * published, uploaded, posted, transmitted, distributed, or disclosed in any way
 * without Intel's prior express written permission.
 *
 * No license under any patent, copyright, trade secret or other intellectual
 * property right is granted to or conferred upon you by disclosure or delivery
 * of the Materials, either expressly, by implication, inducement, estoppel or
 * otherwise. Any license under such intellectual property rights must be express
 * and approved by Intel in writing.
 */

import Vuetify from 'vuetify';
import Vuex from 'vuex';
import sinon from 'sinon';
import VueRouter from 'vue-router'
import {shallowMount, createLocalVue} from '@vue/test-utils';
import ActionHeaderButtons from '../../../../../src/components/ModelsTableFeatures/ActionHeaderButtons';

describe('VUE components ActionHeaderButtons', () => {
  let wrapper, router, props, getters, state, store, localVue;
  beforeEach(function () {
    state = {
      tensorMode: false
    };
    getters = {
      tensorMode: (state) => state.tensorMode
    };
    store = new Vuex.Store({
      state,
      getters
    });
    props = {
      clearSort: sinon.spy(),
      setVisibleColumnsHandler: sinon.spy(),
      selectedByUserColumns: [],
      customizableVisibilityColumns: ['test_01'],
      onLaunchTensorHandler: sinon.spy(),
      onDiscardTensorHandler: sinon.spy(),
      disabled: false
    };
    localVue = createLocalVue();
    localVue.use(Vuex);
    localVue.use(VueRouter);
    localVue.use(Vuetify);
    router = new VueRouter();
    wrapper = shallowMount(ActionHeaderButtons, {propsData: props, router, localVue, store});
  });

  it('Should render action buttons elements correctly', function () {
    expect(wrapper.html().includes('buttons_block')).to.equal(true);
  });

  it('Should call setVisibleColumnsHandler on revert click', function () {
    wrapper.vm.showColumnMgmtModal = true;
    wrapper.vm.revertToDefault();
    expect(wrapper.vm.showColumnMgmtModal).to.equal(false);
    expect(props.setVisibleColumnsHandler.calledTwice).to.equal(true);
    expect(props.setVisibleColumnsHandler.calledWith([])).to.equal(true);
  });

  it('Should call setVisibleColumnsHandler on apply visible headers action', function () {
    wrapper.vm.showColumnMgmtModal = true;
    wrapper.vm.applyVisibleHeaders();
    expect(wrapper.vm.showColumnMgmtModal).to.equal(false);
    expect(props.setVisibleColumnsHandler.calledTwice).to.equal(true);
    expect(props.setVisibleColumnsHandler.calledWith(wrapper.vm.draft)).to.equal(true);
  });

  it('Should prepare draft on selectedByUserColumns update', function () {
    props.headers = ['header1'];
    wrapper = shallowMount(ActionHeaderButtons, {propsData: props, router, localVue, store});
    wrapper.setProps({selectedByUserColumns: ['header1']});
    expect(wrapper.vm.draft).to.deep.equal(wrapper.vm.selectedByUserColumns);
  });

  it('Should add to draft if visible', function () {
    wrapper.vm.showColumn('test');
    expect(wrapper.vm.draft.includes('test')).to.equal(true);
  });

  it('Should remove from draft if hidden', function () {
    wrapper.vm.draft = ['test'];
    wrapper.vm.hideColumn('test');
    expect(wrapper.vm.draft.includes('test')).to.equal(false);
  });

  it('Should clear draft if cancel button clicked', function () {
    wrapper.vm.draft = ['test'];
    wrapper.vm.showColumnMgmtModal = true;
    wrapper.vm.discardVisibleHeaders();
    expect(wrapper.vm.draft).to.deep.equal(wrapper.vm.selectedByUserColumns);
    expect(wrapper.vm.showColumnMgmtModal).to.equal(false);
  });
});
