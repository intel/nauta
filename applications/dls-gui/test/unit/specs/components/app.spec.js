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

import Vue from 'vue';
import Vuex from 'vuex';
import Vuetify from 'vuetify';
import sinon from 'sinon';
import VueRouter from 'vue-router'
import {shallowMount, createLocalVue} from '@vue/test-utils';
import App from '../../../../src/App';

describe('VUE components App', () => {
  let wrapper, router, state, store, getters, localVue;
  beforeEach(function () {
    state = {
      isLogged: true,
      errorType: 'type',
      errorTime: 'time',
      errorContent: 'content',
      tensorMode: false
    };
    getters = {
      isLogged: (state) => state.isLogged,
      errorType: (state) => state.errorType,
      errorTime: (state) => state.errorTime,
      errorContent: (state) => state.errorContent,
      tensorMode: (state) => state.tensorMode
    };
    store = new Vuex.Store({
      state,
      getters
    });
    localVue = createLocalVue();
    localVue.use(Vuex);
    localVue.use(VueRouter);
    localVue.use(Vuetify);
    router = new VueRouter();
    wrapper = shallowMount(App, {store, router, localVue});
  });

  it('Should render div with "app" id', function () {
    expect(wrapper.find('#app').exists()).to.equal(true);
  });

  it('Should call notify', function (done) {
    const notifyMock = sinon.spy();
    wrapper = shallowMount(App, {store, router, localVue, mocks: {$notify: notifyMock, $route: sinon.spy()}});
    wrapper.vm.$store.state.errorType = 'new';
    Vue.nextTick()
      .then(() => {
        expect(notifyMock.called).to.equal(true);
        done()
      }).catch(done);
  });
});
