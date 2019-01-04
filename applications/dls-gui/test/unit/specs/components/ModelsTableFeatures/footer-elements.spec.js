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
