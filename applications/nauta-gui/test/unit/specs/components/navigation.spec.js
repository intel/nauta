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
