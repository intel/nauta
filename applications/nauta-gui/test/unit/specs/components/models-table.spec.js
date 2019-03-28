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
import Vue from 'vue';
import Vuex from 'vuex';
import Vuetify from 'vuetify';
import sinon from 'sinon';
import VueRouter from 'vue-router'
import {shallowMount, createLocalVue} from '@vue/test-utils';
import ModelsTable from '../../../../src/components/ModelsTable';
import Q from 'q';
import messages from '../../../../src/utils/constants/messages';

describe('VUE components ModelsTable', () => {
  let wrapper, router, store, state, getters, actions, localVue, defered, context;
  beforeEach(function () {
    context = {
      messages: messages
    };
    state = {
      experiments: {
        data: [],
        params: ['param1', 'param2', 'param3'],
        stats: {
          total: 0,
          a: 0,
          b: 0,
          pageNumber: 0,
          totalPagesCount: 0,
          filteredDataCount: 0,
          datetime: 0
        }
      },
      selectedExperimentsByUser: [],
      currentlyVisibleColumns: [],
      columnValuesOptions: [],
      columnValuesApplied: [],
      isCheckingAuth: true,
      isInitializedData: true,
      experimentResources: [],
      itemsCountPerPage: 5,
      currentPage: 2,
      refreshInterval: 30,
      allUsersMode: false,
      fetchingDataActive: false,
      isLogged: true,
      initializedDataFlag: true,
      tensorboardLaunching: false,
      username: 'anonymous'
    };
    getters = {
      experimentsData: state => state.experiments.data,
      selectedExperimentsByUser: state => state.selectedExperimentsByUser,
      experimentsParams: state => state.experiments.params,
      currentlyVisibleColumns: state => state.currentlyVisibleColumns,
      columnValuesOptions: state => state.columnValuesOptions,
      columnValuesApplied: state => state.columnValuesApplied,
      experimentsBegin: state => state.experiments.stats.a,
      experimentsTotal: state => state.experiments.stats.total,
      filteredDataCount: state => state.experiments.stats.filteredDataCount,
      experimentsEnd: state => state.experiments.stats.b,
      experimentsPageNumber: state => state.experiments.stats.pageNumber,
      experimentsTotalPagesCount: state => state.experiments.stats.totalPagesCount,
      lastUpdate: state => state.experiments.stats.datetime,
      fetchingDataActive: state => state.fetchingDataActive,
      tensorboardLaunching: state => state.tensorboardLaunching,
      isCheckingAuth: state => state.authLoadingState,
      initializedDataFlag: state => state.initializedDataFlag,
      isLogged: state => state.isLogged,
      username: state => state.username,
      experimentResources: state => state.experimentResources,
      itemsCountPerPage: state => state.itemsCountPerPage,
      currentPage: state => state.currentPage,
      refreshInterval: state => state.refreshInterval,
      allUsersMode: state => state.allUsersMode
    };
    defered = Q.defer();
    actions = {
      getUserExperiments: sinon.spy(),
      clearExperimentSelection: sinon.spy(),
      markExperimentsAsSelected: sinon.spy(),
      markExperimentAsSelected: sinon.spy(),
      showColumns: sinon.spy(),
      showColumn: sinon.spy(),
      showRefreshMessage: sinon.spy(),
      clearAllUsersMode: sinon.spy(),
      launchTensorboard: sinon.spy(),
      getExperimentResources: sinon.stub().returns(defered.promise)
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

  it('Should return "true" as activity status of custom filters if any filter active', function () {
    wrapper.vm.filterByValModals.state.params = [1];
    expect(wrapper.vm.customFiltersActive).to.equal(1);
  });

  it('Should return "false" as activity status of custom filters if any filter active', function () {
    expect(wrapper.vm.customFiltersActive).to.equal(false);
  });

  it('Should return true if tensor btn should be available for exp', function () {
    const type = 'training';
    const result = wrapper.vm.isTensorboardAvailableForExp(type);
    expect(result).to.equal(true);
  });

  it('Should return false if tensor btn should not be available for exp', function () {
    const type = 'inference';
    const result = wrapper.vm.isTensorboardAvailableForExp(type);
    expect(result).to.equal(false);
  });

  it('Should clear namespace filters if showAllUsersData action', function () {
    wrapper.vm.filterByValModals.namespace.params = ['1', '2'];
    wrapper.vm.showAllUsersData();
    expect(wrapper.vm.filterByValModals.namespace.params).to.deep.equal([]);
  });

  it('Should return visible columns (default)', function () {
    expect(wrapper.vm.currentlyVisibleColumns).to.deep.equal([]);
  });

  it('Should get data if search pattern provided', function () {
    wrapper.vm.searchPattern = 'test';
    expect(actions.getUserExperiments.calledTwice).to.equal(true);
  });

  it('Should get data if sorting order updated', function () {
    wrapper.vm.sorting.order = 'asc';
    expect(actions.getUserExperiments.calledTwice).to.equal(true);
  });

  it('Should get data if count of items per page updated', function () {
    wrapper.vm.$store.state.itemsCountPerPage = 23;
    expect(actions.getUserExperiments.calledTwice).to.equal(true);
  });

  it('Should get data if page number updated', function () {
    wrapper.vm.$store.state.currentPage = 23;
    expect(actions.getUserExperiments.calledTwice).to.equal(true);
  });

  it('Should clear sort params on clear sort action', function () {
    wrapper.vm.activeColumnIdx = 999;
    wrapper.vm.activeColumnName = '999';
    wrapper.vm.clearSort();
    expect(wrapper.vm.activeColumnIdx).to.equal(0);
    expect(wrapper.vm.activeColumnName).to.equal('creationTimestamp');
  });

  it('Should call markExperimentAsSelected on exp select', function () {
    const selectedExp = 'exp';
    wrapper.vm.selectExp({data: [selectedExp]});
    expect(actions.markExperimentAsSelected.calledOnce).to.equal(true);
  });

  it('Should call markExperimentsAsSelected on exp deselect', function () {
    const selectedExp = {attributes:{name: 'test'}};
    wrapper.vm.deselectExp(selectedExp);
    expect(actions.markExperimentsAsSelected.calledOnce).to.equal(true);
  });

  it('Should check is selected item correctly', function () {
    const selectedExp = {attributes:{name: 'test'}};
    wrapper.vm.$store.state.selectedExperimentsByUser = [selectedExp];
    const result = wrapper.vm.isSelected(selectedExp);
    expect(result).to.deep.equal(true);
  });

  it('Should not refresh data if younger than 30s', function () {
    Date.now = sinon.stub().returns(1528190409842);
    wrapper.vm.$store.state.experiments.stats.datetime = 1528190409842;
    wrapper.vm.timer(context);
    expect(actions.getUserExperiments.calledOnce).to.equal(true);
    expect(actions.showRefreshMessage.called).to.equal(true);
  });

  it('Should refresh data if older than 30s', function () {
    Date.now = sinon.stub().returns(1528190409842);
    wrapper.vm.$store.state.experiments.stats.datetime = 1128190409842;
    wrapper.vm.timer(context);
    expect(actions.getUserExperiments.calledTwice).to.equal(true);
    expect(actions.showRefreshMessage.called).to.equal(true);
  });

  it('Should not refresh data if older than 30s but request is pending', function () {
    Date.now = sinon.stub().returns(1528190409842);
    wrapper.vm.$store.state.experiments.stats.datetime = 1128190409842;
    wrapper.vm.$store.state.fetchingDataActive = true;
    wrapper.vm.timer(context);
    expect(actions.getUserExperiments.calledOnce).to.equal(true);
    expect(actions.showRefreshMessage.called).to.equal(true);
  });

  it('Should clear all filters on clear action', function () {
    wrapper.vm.filterByValModals.name.params = [1,2,3,4];
    wrapper.vm.clearFilter();
    expect(wrapper.vm.filterByValModals.name.params).to.deep.equal([]);
  });

  it('Should not format unknown value', function () {
    const value = 4;
    const result = wrapper.vm.parseValue('test', value);
    expect(result).to.deep.equal(value);
  });

  it('Should return default string if trainingStartTime value empty', function () {
    const value = null;
    const expectedResult = '---';
    const result = wrapper.vm.parseValue('trainingStartTime', value);
    expect(result).to.deep.equal(expectedResult);
  });

  it('Should return correct duration time for training', function () {
    const trainingDurationTime = 262861000;
    const expectedResult = '3 days, 1 hrs, 1 mins, 1 s';
    const result = wrapper.vm.parseValue('trainingDurationTime', trainingDurationTime);
    expect(result).to.deep.equal(expectedResult);
  });

  it('Should return correct training time in queue for training', function () {
    const trainingTimeInQueue = 0;
    const expectedResult = '---';
    const result = wrapper.vm.parseValue('trainingTimeInQueue', trainingTimeInQueue);
    expect(result).to.deep.equal(expectedResult);
  });

  it('Should return default string if training duration time is a negative value', function () {
    const trainingDurationTime = -262861000;
    const expectedResult = '0 days, 0 hrs, 0 mins, 0 s';
    const result = wrapper.vm.parseValue('trainingDurationTime', trainingDurationTime);
    expect(result).to.deep.equal(expectedResult);
  });

  it('Should return default string if training type is an empty value', function () {
    const type = null;
    const expectedResult = '-';
    const result = wrapper.vm.parseValue('type', type);
    expect(result).to.deep.equal(expectedResult);
  });

  it('Should return upper cased string if training type is a string value', function () {
    const type = 'inference';
    const expectedResult = 'Inference';
    const result = wrapper.vm.parseValue('type', type);
    expect(result).to.deep.equal(expectedResult);
  });

  it('Should return default string if parameters is an empty value', function () {
    const parameters = null;
    const expectedResult = '--';
    const result = wrapper.vm.parseValue('parameters', parameters);
    expect(result).to.deep.equal(expectedResult);
  });

  it('Should return proper string if parameters is an array', function () {
    const parameters = ['arg1', '-p', 'test'];
    const expectedResult = 'arg1, -p, test';
    const result = wrapper.vm.parseValue('parameters', parameters);
    expect(result).to.deep.equal(expectedResult);
  });

  it('Should hide filter windows before showing others', function () {
    wrapper.vm.filterByValModals.name.visible = true;
    wrapper.vm.switchFilterWindow('namespace', true);
    expect(wrapper.vm.filterByValModals.name.visible).to.deep.equal(false);
  });

  it('Should set filters on apply click', function () {
    wrapper.vm.filterByValModals.name.visible = true;
    const draft = [1, 2, 3, 4, 5];
    wrapper.vm.onApplyValuesColumnFilter('name', draft);
    expect(wrapper.vm.filterByValModals.name.params).to.deep.equal(draft);
    expect(wrapper.vm.filterByValModals.name.visible).to.deep.equal(false);
  });

  it('Should return label for header if key is known', function () {
    const headerKey = 'name';
    const label = wrapper.vm.getLabel(headerKey);
    expect(label).to.not.equal(headerKey);
  });

  it('Should return headerKey for header if key is unknown', function () {
    const headerKey = 'xyz';
    const expectedHeaderKey = 'Xyz';
    const label = wrapper.vm.getLabel(headerKey);
    expect(label).to.equal(expectedHeaderKey);
  });

  it('Should return false if column is invisible', function () {
    const columnName = 'param3';
    const result = wrapper.vm.isVisibleColumn(columnName);
    expect(result).to.equal(false);
  });

  it('Should return true if column is visible', function () {
    const columnName = 'param3';
    wrapper.vm.$store.state.currentlyVisibleColumns = [columnName];
    const result = wrapper.vm.isVisibleColumn(columnName);
    expect(result).to.equal(true);
  });

  it('Should call showColumns if column marked as visible', function () {
    const columnName = 'param3';
    const result = wrapper.vm.setVisibleColumns(columnName);
    expect(actions.showColumns.calledOnce).to.equal(true);
  });

  it('Should return true if column is filterable by value', function () {
    const columnName = 'name';
    const result = wrapper.vm.isFilterableByValColumn(columnName);
    expect(result).to.equal(true);
  });

  it('Should return false if column is filterable by value', function () {
    const columnName = 'xyz';
    const result = wrapper.vm.isFilterableByValColumn(columnName);
    expect(result).to.equal(false);
  });

  it('Should return false if details invisible', function () {
    const expName = 'xyz';
    const result = wrapper.vm.areDetailsVisible(expName);
    expect(result).to.equal(false);
  });

  it('Should return true if details visible', function () {
    const expName = 'xyz';
    wrapper.vm.visibleDetails.push(expName);
    const result = wrapper.vm.areDetailsVisible(expName);
    expect(result).to.equal(true);
  });

  it('Should set flags when order toggled', function () {
    const idx = '2';
    const toggledColumnName = 'name2';
    const expectedSortingOrder = 'desc';
    const expectedSortingIcon = 'arrow_downward';
    wrapper.vm.activeColumnIdx = 999;
    wrapper.vm.activeColumnName = 'name999';
    wrapper.vm.sorting.order = 'asc';
    wrapper.vm.sorting.currentSortIcon = 'arrow_upward';
    wrapper.vm.toggleOrder(toggledColumnName, idx);
    expect(wrapper.vm.activeColumnIdx).to.equal(idx);
    expect(wrapper.vm.activeColumnName).to.equal(toggledColumnName);
    expect(wrapper.vm.sorting.order).to.equal(expectedSortingOrder);
    expect(wrapper.vm.sorting.currentSortIcon).to.equal(expectedSortingIcon);
  });

  it('Should add exp to visibility list if not visible', function (done) {
    const expName = 'xyz';
    wrapper.vm.toggleDetails(expName);
    defered.resolve();
    process.nextTick(() => {
      expect(wrapper.vm.visibleDetails.includes(expName)).to.equal(true);
      done();
    });
  });

  it('Should remove exp from visibility list if visible', function (done) {
    const expName = 'xyz';
    wrapper.vm.visibleDetails.push(expName);
    wrapper.vm.toggleDetails(expName);
    defered.resolve();
    process.nextTick(() => {
      expect(wrapper.vm.visibleDetails.includes(expName)).to.equal(false);
      done();
    });
  });

  it('Should refresh experiments resources data if any details visible', function (done) {
    const expName = 'xyz';
    wrapper.vm.visibleDetails.push(expName);
    wrapper.vm.getData(expName);
    process.nextTick(() => {
      expect(actions.getExperimentResources.calledTwice).to.equal(true); // first on component init, second on getData
      done();
    });
  });
});
