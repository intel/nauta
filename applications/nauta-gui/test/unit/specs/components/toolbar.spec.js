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
      tensorMode: () => 'username',
      menuBtnVisibility: () => true
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
