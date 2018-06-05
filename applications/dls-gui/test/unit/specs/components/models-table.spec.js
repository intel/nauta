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

import Vue from 'Vue';
import Vuex from 'vuex';
import Vuetify from 'vuetify';
import sinon from 'sinon';
import VueRouter from 'vue-router'
import {shallowMount, createLocalVue} from '@vue/test-utils';
import ModelsTable from '../../../../src/components/ModelsTable';

describe('VUE components ModelsTable', () => {
  let wrapper, router, store, state, getters, actions, localVue;
  beforeEach(function () {
    state = {
      fetchingDataActive: false,
      experiments: {
        data: [],
        params: ['param1', 'param2', 'param3'],
        stats: {
          total: 0,
          a: 0,
          b: 0,
          pageNumber: 0,
          totalPagesCount: 0,
          datetime: 0
        }
      },
      tensorMode: false
    };
    getters = {
      experimentsData: state => state.experiments.data,
      experimentsParams: state => state.experiments.params,
      experimentsBegin: state => state.experiments.stats.a,
      experimentsTotal: state => state.experiments.stats.total,
      experimentsEnd: state => state.experiments.stats.b,
      experimentsPageNumber: state => state.experiments.stats.pageNumber,
      experimentsTotalPagesCount: state => state.experiments.stats.totalPagesCount,
      lastUpdate: state => state.experiments.stats.datetime,
      fetchingDataActive: state => state.fetchingDataActive,
      tensorMode: state => state.tensorMode,
    };
    actions = {
      getUserExperiments: sinon.spy(),
      enableTensorMode: sinon.spy(),
      disableTensorMode: sinon.spy()
    };
    store = new Vuex.Store({
      state,
      actions,
      getters
    });
    localVue = createLocalVue();
    localVue.use(Vuex);
    localVue.use(VueRouter);
    localVue.use(Vuetify);
    router = new VueRouter();
    setInterval = sinon.spy();
    clearInterval = sinon.spy();
    wrapper = shallowMount(ModelsTable, {store, router, localVue});
  });

  it('Should clearInterval on destroy correctly', function () {
    expect(setInterval.calledOnce).to.equal(true);
    wrapper.destroy();
    expect(clearInterval.calledOnce).to.equal(true);
  });

  it('Should return pagination stats correctly', function () {
    const expectedResult = `${state.experiments.stats.a}-${state.experiments.stats.b} of ${state.experiments.stats.total}`;
    expect(wrapper.vm.paginationStats).to.equal(expectedResult);
  });

  it('Should return visible columns (default)', function () {
    expect(wrapper.vm.visibleColumns).to.deep.equal(state.experiments.params);
  });

  it('Should return visible columns (one hidden)', function () {
    wrapper.vm.hiddenColumns = ['param1'];
    expect(wrapper.vm.visibleColumns).to.not.deep.equal(state.experiments.params);
    expect(wrapper.vm.visibleColumns.indexOf('param1')).to.equal(-1);
  });

  it('Should get data if search pattern provided', function () {
    wrapper.vm.searchPattern = 'test';
    expect(actions.getUserExperiments.calledTwice).to.equal(true);
  });

  it('Should get data if sorting order updated', function () {
    wrapper.vm.sorting.order = 'desc';
    expect(actions.getUserExperiments.calledTwice).to.equal(true);
  });

  it('Should get data if count of items per page updated', function () {
    wrapper.vm.pagination.itemsCountPerPage = 23;
    expect(actions.getUserExperiments.calledTwice).to.equal(true);
  });

  it('Should get data if page number updated', function () {
    wrapper.vm.pagination.currentPage = 23;
    expect(actions.getUserExperiments.calledTwice).to.equal(true);
  });

  it('Should update currentPage if stats provided from backend', function (done) {
    wrapper.vm.$store.state.experiments.stats.pageNumber = 24;
    Vue.nextTick()
      .then(() => {
        expect(wrapper.vm.pagination.currentPage).to.equal(24);
        done()
      }).catch(done);
  });

  it('Should cut text if too long', function () {
    const longText = 'veeeeeerrrryyyyyy looooooongggg texttt';
    const expectedResult = 'veeeeeerrrryyy...';
    const result = wrapper.vm.cutLongText(longText);
    expect(result).to.equal(expectedResult);
  });

  it('Should not cut text if not too long', function () {
    const notLongText = 'veeeeeerrrry';
    const expectedResult = notLongText;
    const result = wrapper.vm.cutLongText(notLongText);
    expect(result).to.equal(expectedResult);
  });

  it('Should not cut text if not too long', function () {
    const column = 'column1';
    const idx = 1;
    wrapper.vm.toggleOrder(column, idx);
    expect(wrapper.vm.activeColumnIdx).to.equal(idx);
    expect(wrapper.vm.activeColumnName).to.equal(column);
  });

  it('Should clear sort params on clear sort action', function () {
    wrapper.vm.activeColumnIdx = 999;
    wrapper.vm.activeColumnName = '999';
    wrapper.vm.clearSort();
    expect(wrapper.vm.activeColumnIdx).to.equal(null);
    expect(wrapper.vm.activeColumnName).to.equal(null);
  });

  it('Should set pagination params if count of rows per page updated', function () {
    const currentCount = 50;
    wrapper.vm.updateCountPerPage(currentCount);
    expect(wrapper.vm.pagination.itemsCountPerPage).to.equal(currentCount);
    expect(wrapper.vm.pagination.currentPage).to.equal(1);
  });

  it('Should decrement currentPage if previous page', function () {
    const currentPage = 100;
    wrapper.vm.pagination.currentPage = currentPage;
    wrapper.vm.previousPage();
    expect(wrapper.vm.pagination.currentPage).to.equal(currentPage - 1);
  });

  it('Should increment currentPage if previous page', function () {
    const currentPage = 100;
    wrapper.vm.pagination.currentPage = currentPage;
    wrapper.vm.nextPage();
    expect(wrapper.vm.pagination.currentPage).to.equal(currentPage + 1);
  });

  it('Should set hidden columns', function () {
    const hiddenColumns = [1, 2, 3];
    wrapper.vm.setHiddenColumns(hiddenColumns);
    expect(wrapper.vm.hiddenColumns).to.deep.equal(hiddenColumns);
  });

  it('Should call enableTensorMode on launch btn click', function () {
    wrapper.vm.launchTensorboard();
    expect(actions.enableTensorMode.calledOnce).to.equal(true);
  });

  it('Should call disableTensorMode on exit btn click', function () {
    wrapper.vm.discardTensorboard();
    expect(actions.disableTensorMode.calledOnce).to.equal(true);
    expect(wrapper.vm.selected).to.deep.equal([]);
  });

  it('Should call disableTensorMode on exit btn click', function () {
    wrapper.vm.discardTensorboard();
    expect(actions.disableTensorMode.calledOnce).to.equal(true);
    expect(wrapper.vm.selected).to.deep.equal([]);
  });

  it('Should add exp to selected list', function () {
    const selectedExp = 'exp';
    wrapper.vm.selectExp(selectedExp);
    expect(wrapper.vm.selected).to.deep.equal([selectedExp]);
  });

  it('Should delete exp from selected list on deselect', function () {
    const selectedExp = {name: 'test'};
    wrapper.vm.selected = [selectedExp];
    wrapper.vm.deselectExp(selectedExp);
    expect(wrapper.vm.selected).to.deep.equal([]);
  });

  it('Should check is selected item correctly', function () {
    const selectedExp = {name: 'test'};
    wrapper.vm.selected = [selectedExp];
    const result = wrapper.vm.isSelected(selectedExp);
    expect(result).to.deep.equal(true);
  });

  it('Should not refresh data if younger than 30s', function () {
    Date.now = sinon.stub().returns(1528190409842);
    wrapper.vm.$store.state.experiments.stats.datetime = 1528190409842;
    wrapper.vm.timer();
    expect(actions.getUserExperiments.calledOnce).to.equal(true);
    expect(wrapper.vm.refresh.lastUpdateLabel).to.equal('Last updated moment ago.');
  });

  it('Should refresh data if older than 30s', function () {
    Date.now = sinon.stub().returns(1528190409842);
    wrapper.vm.$store.state.experiments.stats.datetime = 1128190409842;
    wrapper.vm.timer();
    expect(actions.getUserExperiments.calledTwice).to.equal(true);
    expect(wrapper.vm.refresh.lastUpdateLabel).to.equal('Last updated over 30 seconds ago.');
  });

  it('Should not refresh data if older than 30s but request is pending', function () {
    Date.now = sinon.stub().returns(1528190409842);
    wrapper.vm.$store.state.experiments.stats.datetime = 1128190409842;
    wrapper.vm.$store.state.fetchingDataActive = true;
    wrapper.vm.timer();
    expect(actions.getUserExperiments.calledOnce).to.equal(true);
    expect(wrapper.vm.refresh.lastUpdateLabel).to.equal('Last updated over 30 seconds ago.');
  });
});
