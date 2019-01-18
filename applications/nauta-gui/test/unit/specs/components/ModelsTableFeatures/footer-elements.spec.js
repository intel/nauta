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
import FooterElements from '../../../../../src/components/ModelsTableFeatures/FooterElements';

describe('VUE components FooterElements', () => {
  let wrapper, router, props, localVue;
  beforeEach(function () {
    props = {
      updateCountHandler: sinon.spy(),
      currentPage: 1,
      pagesCount: 1,
      nextPageAction: sinon.spy(),
      prevPageAction: sinon.spy(),
      paginationStats: 'stats',
      lastUpdateLabel: 'moment ago'
    };
    localVue = createLocalVue();
    localVue.use(VueRouter);
    localVue.use(Vuetify);
    router = new VueRouter();
    wrapper = shallowMount(FooterElements, {propsData: props, router, localVue});
  });

  it('Should render footer elements correctly', function () {
    expect(wrapper.text().includes(props.paginationStats)).to.equal(true);
    expect(wrapper.text().includes(props.lastUpdateLabel)).to.equal(true);
    expect(wrapper.text().includes('Rows per page')).to.equal(true);
  });

  it('Should call updateCountHandler if select switched', function () {
    wrapper.vm.chosenCount = 10;
    expect(props.updateCountHandler.calledOnce).to.equal(true);
  });
});
