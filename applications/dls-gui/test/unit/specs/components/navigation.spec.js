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
import Nav from '../../../../src/components/Navigation';

describe('VUE components Navigation', () => {
  let wrapper, router, store, getters, actions, mutations, localVue, addEventMock, removeEventMock;
  beforeEach(function () {
    getters = {
      tensorMode: () => true,
      username: () => 'username',
      menuVisibility: () => true
    };
    actions = {
      logIntoK8SDashboard: sinon.spy()
    };
    mutations = {
      setMenuVisibility: sinon.spy()
    };
    store = new Vuex.Store({
      actions,
      getters,
      mutations
    });
    localVue = createLocalVue();
    localVue.use(Vuex);
    localVue.use(VueRouter);
    localVue.use(Vuetify);
    addEventMock = sinon.stub(document, 'addEventListener');
    removeEventMock = sinon.stub(document, 'removeEventListener');
    router = new VueRouter();
    wrapper = shallowMount(Nav, {store, router, localVue});
  });

  afterEach(function () {
    addEventMock.restore();
    removeEventMock.restore();
  });

  it('Should call addEventListener on component create action', function () {
    expect(addEventMock.calledOnce).to.equal(true);
  });

  it('Should call logIntoK8SDashboard method when go to k8s dashboard', function () {
    wrapper.vm.goToK8sDashboard();
    expect(actions.logIntoK8SDashboard.calledOnce).to.equal(true);
  });

  it('Should call removeEventListener on component destroy action', function () {
    wrapper.destroy();
    expect(removeEventMock.calledOnce).to.equal(true);
  });

  it('Should call setMenuVisibility if not clicked on sidebar', function () {
    wrapper.vm.$refs = {
      navelement: {
        $vnode: {
          elm: 'sidebar'
        }
      }
    };
    const e = {
      target: 'body'
    };
    wrapper.vm.documentClick(e);
    expect(mutations.setMenuVisibility.calledOnce).to.equal(true);
    expect(mutations.setMenuVisibility.getCall(0).args[1]).to.equal(false);
  });

  it('Should not call setMenuVisibility if clicked on sidebar', function () {
    wrapper.vm.$refs = {
      navelement: {
        $vnode: {
          elm: 'sidebar'
        }
      }
    };
    const e = {
      target: 'sidebar'
    };
    wrapper.vm.documentClick(e);
    expect(mutations.setMenuVisibility.called).to.equal(false);
  });
});
