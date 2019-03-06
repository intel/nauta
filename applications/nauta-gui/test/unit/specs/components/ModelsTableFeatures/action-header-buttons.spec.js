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
      columns: ['name', 'state', 'creationTimestamp', 'trainingStartTime', 'trainingDurationTime',
        'type', 'test_01'],
      alwaysVisibleColumns: ['name', 'state'],
      initiallyVisibleColumns: ['name', 'state', 'creationTimestamp', 'trainingStartTime', 'trainingDurationTime',
        'type'],
      onLaunchTensorHandler: sinon.spy(),
      onDiscardTensorHandler: sinon.spy(),
      setIntervalHandler: sinon.spy(),
      refreshNowHandler: sinon.spy(),
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
    const initiallyVisibleColumns = ['name', 'state', 'creationTimestamp', 'trainingStartTime', 'trainingDurationTime',
        'type'];
    wrapper.vm.showColumnMgmtModal = true;
    wrapper.vm.revertToDefault();
    expect(wrapper.vm.showColumnMgmtModal).to.equal(false);
    expect(props.setVisibleColumnsHandler.calledTwice).to.equal(true);
    expect(props.setVisibleColumnsHandler.calledWith(props.initiallyVisibleColumns)).to.equal(true);
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
    expect(wrapper.vm.draft).to.deep.equal(wrapper.vm.selectedByUserColumns);
    expect(wrapper.vm.showColumnMgmtModal).to.equal(false);
  });

  it('Should call setIntervalHandler if new refresh interval value has been set', function () {
    const value = 60;
    wrapper.vm.setRefreshIntervalValue(value);
    expect(props.setIntervalHandler.calledOnce).to.equal(true);
    expect(props.setIntervalHandler.calledWith(value)).to.equal(true);
  });
});
