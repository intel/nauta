/**
 * Copyright (c) 2019 Intel Corporation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
import Vue from 'vue';
import Vuex from 'vuex';
import Vuetify from 'vuetify';
import Notifications from 'vue-notification';
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
    localVue.use(Notifications);
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
