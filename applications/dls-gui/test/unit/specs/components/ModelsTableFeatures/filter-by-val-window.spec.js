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
