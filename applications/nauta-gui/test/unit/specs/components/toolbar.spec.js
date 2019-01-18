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

import Vuex from 'vuex';
import Vuetify from 'vuetify';
import sinon from 'sinon';
import VueRouter from 'vue-router'
import {shallowMount, createLocalVue} from '@vue/test-utils';
import Toolbar from '../../../../src/components/Toolbar';

describe('VUE components Toolbar', () => {
  let wrapper, router, store, getters, actions, localVue;
  beforeEach(function () {
    getters = {
      username: () => 'username',
      getMenuParams: () => {
        return {btnVisible: true}
      },
      getUserboxParams: () => {
        return {visible: true}
      },
      tensorMode: () => 'username'
    };
    actions = {
      toggleMenu: sinon.spy(),
      handleLogOut: sinon.spy()
    };
    store = new Vuex.Store({
      actions,
      getters
    });
    localVue = createLocalVue();
    localVue.use(Vuex);
    localVue.use(VueRouter);
    localVue.use(Vuetify);
    router = new VueRouter();
    wrapper = shallowMount(Toolbar, {store, router, localVue});
  });

  it('Should clear auth data on logout', function () {
    wrapper.vm.onSingOutBtnClick();
    expect(actions.handleLogOut.calledOnce).to.equal(true);
  });
});
