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
import FilterByValWindow from '../../../../../src/components/ModelsTableFeatures/FilterByValWindow';

describe('VUE components FilterByValWindow', () => {
  let wrapper, router, props, localVue;
  beforeEach(function () {
    props = {
      onCloseClickHandler: sinon.spy(),
      onApplyClickHandler: sinon.spy(),
      options: ['aa', 'bb', 'cc'],
      appliedOptions: [],
      columnName: 'test'
    };
    localVue = createLocalVue();
    localVue.use(VueRouter);
    localVue.use(Vuetify);
    router = new VueRouter();
    wrapper = shallowMount(FilterByValWindow, {propsData: props, router, localVue});
  });

  it('Should render action buttons elements correctly', function () {
    expect(wrapper.html().includes('filter-box elevation-3')).to.equal(true);
  });

  it('Should filter box options if search pattern provided', function () {
    wrapper.vm.searchPattern = 'a';
    expect(wrapper.vm.boxOptions).to.deep.equal(['aa']);
  });

  it('Should deselect chosen options', function () {
    wrapper.vm.chosenOptions = [1, 2, 3, 4];
    wrapper.vm.deselectAll();
    expect(wrapper.vm.chosenOptions).to.deep.equal([]);
  });

  it('Should select all possible options', function () {
    wrapper.vm.selectAll();
    expect(wrapper.vm.chosenOptions).to.deep.equal(props.options);
  });

  it('Should select item if not selected', function () {
    wrapper.vm.switchOption('option1');
    expect(wrapper.vm.chosenOptions.includes('option1')).to.equal(true);
  });

  it('Should deselect item if selected', function () {
    wrapper.vm.chosenOptions = props.options;
    wrapper.vm.switchOption('aa');
    expect(wrapper.vm.chosenOptions.includes('aa')).to.equal(false);
  });

  it('Should call onCloseClickHandler on close action', function () {
    wrapper.vm.onCloseAction();
    expect(props.onCloseClickHandler.calledOnce).to.equal(true);
  });

  it('Should call onCloseClickHandler on apply action', function () {
    wrapper.vm.onApplyAction();
    expect(props.onApplyClickHandler.calledOnce).to.equal(true);
  });

  it('Should increase limit of visible options on load more action', function () {
    const initialLimit = 10;
    const expectedLimit = 20;
    expect(wrapper.vm.pagination.b).to.equal(initialLimit);
    wrapper.vm.onLoadMoreAction();
    expect(wrapper.vm.pagination.b).to.equal(expectedLimit);
  });
});
