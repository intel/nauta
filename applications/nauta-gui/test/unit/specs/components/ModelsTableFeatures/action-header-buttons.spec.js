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
import Vuetify from 'vuetify';
import sinon from 'sinon';
import VueRouter from 'vue-router'
import {shallowMount, createLocalVue} from '@vue/test-utils';
import ActionHeaderButtons from '../../../../../src/components/ModelsTableFeatures/ActionHeaderButtons';
import Vuex from "vuex";

describe('VUE components ActionHeaderButtons', () => {
  let wrapper, router, props, getters, actions, state, store, localVue;
  beforeEach(function () {
    state = {
      experimentsParams: [],
      selectedExperimentsByUser: [],
      currentlyVisibleColumns: [],
      allUsersMode: false,
      refreshInterval: 30
    };
    getters = {
      experimentsParams: state => state.experimentsParams,
      selectedExperimentsByUser: state => state.selectedExperimentsByUser,
      currentlyVisibleColumns: state => state.currentlyVisibleColumns,
      allUsersMode: state => state.allUsersMode,
      refreshInterval: state => state.refreshInterval
    };
    actions = {
      showColumns: sinon.spy(),
      clearColumnsSelection: sinon.spy(),
      switchAllUsersMode: sinon.spy(),
      updateRefreshInterval: sinon.spy()
    };
    store = new Vuex.Store({
      state,
      actions,
      getters
    });
    props = {
      clearSort: sinon.spy(),
      onLaunchTensorHandler: sinon.spy(),
      refreshNowHandler: sinon.spy(),
      clearFilterHandler: sinon.spy()
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

  it('Should call this.clearColumnsSelection on revert click', function () {
    wrapper.vm.showColumnMgmtModal = true;
    wrapper.vm.revertToDefault();
    expect(wrapper.vm.showColumnMgmtModal).to.equal(false);
    expect(actions.clearColumnsSelection.calledOnce).to.equal(true);
  });

  it('Should call showColumns on apply visible headers action', function () {
    wrapper.vm.showColumnMgmtModal = true;
    wrapper.vm.applyVisibleHeaders();
    expect(wrapper.vm.showColumnMgmtModal).to.equal(false);
    expect(actions.showColumns.calledOnce).to.equal(true);
  });

  it('Should add to draft if visible', function () {
    wrapper.vm.switchColumn('test');
    expect(wrapper.vm.draft.includes('test')).to.equal(true);
  });

  it('Should remove from draft if hidden', function () {
    wrapper.vm.draft = ['test'];
    wrapper.vm.switchColumn('test');
    expect(wrapper.vm.draft.includes('test')).to.equal(false);
  });

  it('Should clear draft if cancel button clicked', function () {
    wrapper.vm.draft = ['test'];
    wrapper.vm.showColumnMgmtModal = true;
    wrapper.vm.discardVisibleHeaders();
    expect(wrapper.vm.draft).to.deep.equal(wrapper.vm.currentlyVisibleColumns);
    expect(wrapper.vm.showColumnMgmtModal).to.equal(false);
  });

  it('Should call updateRefreshInterval if new refresh interval value has been set', function () {
    const value = 60;
    wrapper.vm.setRefreshIntervalValue(value);
    expect(actions.updateRefreshInterval.calledOnce).to.equal(true);
  });

  it('Should return true if hidden', function () {
    const header = 'test';
    wrapper.vm.draft = [];
    const result = wrapper.vm.isHidden(header);
    expect(result).to.equal(true);
  });

  it('Should return true if always visible', function () {
    const header = 'name';
    const result = wrapper.vm.isAlwaysVisible(header);
    expect(result).to.deep.equal(true);
  });

  it('Should switch modal flag', function () {
    wrapper.vm.showColumnMgmtModal = true;
    wrapper.vm.showColumnMgmtModalHandler();
    expect(wrapper.vm.showColumnMgmtModal).to.equal(false);
  });

  it('Should get label for key', function () {
    const key = 'test';
    const expectedLabel = 'Test';
    const result = wrapper.vm.getLabel(key);
    expect(result).to.equal(expectedLabel);
  });

  it('Should cut label if too long', function () {
    const label = 'Nauta is the best application ever';
    const expectedLabel = 'Nauta is the b...';
    const result = wrapper.vm.cutLongText(label, 14);
    expect(result).to.equal(expectedLabel);
  });

  it('Should not cut label if not too long', function () {
    const label = 'Nauta';
    const expectedLabel = 'Nauta';
    const result = wrapper.vm.cutLongText(label, 14);
    expect(result).to.equal(expectedLabel);
  });

});
