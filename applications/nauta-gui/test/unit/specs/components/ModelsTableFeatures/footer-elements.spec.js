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
import Vuex from "vuex";

describe('VUE components FooterElements', () => {
  let wrapper, router, props, localVue, state, getters, actions, store;
  beforeEach(function () {
    state = {
      experimentsTotalPagesCount: 3,
      experimentsBegin: 1,
      experimentsEnd: 5,
      filteredDataCount: 5,
      itemsCountPerPage: 5,
      currentPage: 1,
      experimentsPageNumber: 1,
      refreshMessage: ''
    };
    getters = {
      experimentsTotalPagesCount: state => state.experimentsTotalPagesCount,
      experimentsBegin: state => state.experimentsBegin,
      experimentsEnd: state => state.experimentsEnd,
      filteredDataCount: state => state.filteredDataCount,
      itemsCountPerPage: state => state.itemsCountPerPage,
      currentPage: state => state.currentPage,
      experimentsPageNumber: state => state.experimentsPageNumber,
      refreshMessage: state => state.refreshMessage
    };
    actions = {
      updatePageNumber: sinon.spy(),
      updateItemsCountPerPage: sinon.spy()
    };
    store = new Vuex.Store({
      state,
      actions,
      getters
    });
    localVue = createLocalVue();
    localVue.use(VueRouter);
    localVue.use(Vuetify);
    router = new VueRouter();
    wrapper = shallowMount(FooterElements, {store, router, localVue});
  });

  it('Should render footer elements correctly', function () {
    expect(wrapper.text().includes(state.refreshMessage)).to.equal(true);
    expect(wrapper.text().includes('Rows per page')).to.equal(true);
  });

  it('Should call updateCountPerPage if select switched', function () {
    wrapper.vm.chosenCount = 10;
    expect(actions.updatePageNumber.calledOnce).to.equal(true);
  });

  it('Should call updateCountPerPage if experimentsPageNumber updated', function () {
    wrapper.vm.$store.state.experimentsPageNumber = 10;
    expect(actions.updatePageNumber.calledOnce).to.equal(true);
  });

  it('Should call setPageAction if onPageNoInputChange called', function () {
    const e = {
      target: {
        value: 4
      }
    };
    wrapper.vm.onPageNoInputChange(e);
    expect(actions.updatePageNumber.calledOnce).to.equal(true);
  });

  it('Should call setPageAction properly if onPageNoInputChange called with negative number', function () {
    const e = {
      target: {
        value: -4
      }
    };
    wrapper.vm.onPageNoInputChange(e);
    expect(actions.updatePageNumber.calledOnce).to.equal(true);
  });

  it('Should set v-model value properly using computed variable', function () {
    const newValue = 5;
    expect(wrapper.vm.chosenPageNo).to.equal(state.currentPage);
    wrapper.vm.chosenPageNo = newValue;
  });

  it('Should call updatePageNumber if previous page', function () {
    wrapper.vm.previousPage();
    expect(actions.updatePageNumber.calledOnce).to.equal(true);
  });

  it('Should call updatePageNumber if next page', function () {
    wrapper.vm.nextPage();
    expect(actions.updatePageNumber.calledOnce).to.equal(true);
  });
});
