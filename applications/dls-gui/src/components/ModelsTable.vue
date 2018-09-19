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

<template>
    <v-layout row wrap>
      <v-container
        v-if="!isLogged || (!isInitializedData && fetchingDataActive) || (isInitializedData && tensorboardLaunching)"
        fill-height justify-center>
        <v-progress-circular :size="90" indeterminate color="warning">
          {{ labels.LOADING }}...
        </v-progress-circular>
      </v-container>
      <v-flex v-if="isLogged && isInitializedData && !tensorboardLaunching" xs12>
        <v-card>
          <v-card-title>
            <h2>{{ labels.EXPERIMENTS }}</h2>
            <v-spacer></v-spacer>
            <ActionHeaderButtons v-if="experimentsTotal !== 0"
              :clearSort="clearSort"
              :clearFilterHandler="clearFilter"
              :selectedByUserColumns="selectedByUserColumns"
              :customizableVisibilityColumns="customizableVisibilityColumns"
              :setVisibleColumnsHandler="setVisibleColumns"
              :onLaunchTensorHandler="onLaunchTensorboardClick"
              :launchTensorDisabled="!tensorBtnAvailable"
            ></ActionHeaderButtons>
            <v-flex xs12 md3 v-if="(experimentsTotal !== 0 || searchPattern)">
              <v-card-title>
                <v-text-field append-icon="search" single-line hide-details v-model="searchPattern"></v-text-field>
              </v-card-title>
            </v-flex>
          </v-card-title>
          <div class="elevation">
            <div v-bind:class="{overflow: filteredDataCount !== 0, 'table-style': true, 'static-height': filterByValWindowVisible }">
              <table class="datatable table">
                <thead>
                <tr>
                  <th width="55px">
                    <div class="select-icon"></div>
                  </th>
                  <th v-for="(header, idx) in experimentsParams" v-if="isVisibleColumn(header)" :id="header" v-bind:key="header"
                      @mouseover="hoveredColumnIdx = idx" @mouseleave="hoveredColumnIdx = null" width="210px">
                    <div class="filter-icon">
                      <v-icon v-if="isFilterableByValColumn(header)" v-on:click="switchFilterWindow(header, true)" small class="pointer-btn">{{ filterIcon }}</v-icon>
                      <FilterByValWindow v-if="filterByValModals[header] && filterByValModals[header].visible"
                                         :column-name="header"
                                         :options="columnValuesOptions[header]"
                                         :onCloseClickHandler="switchFilterWindow"
                                         :onApplyClickHandler="onApplyValuesColumnFilter"
                                         :appliedOptions="columnValuesApplied[header]"
                      >
                      </FilterByValWindow>
                    </div>
                    <div class="cell-title">
                      <v-tooltip bottom>
                        <span slot="activator" v-bind:class="{active: activeColumnName === header}">
                          {{ getLabel(header) }}
                        </span>
                        <span>{{ getLabel(header) }}</span>
                      </v-tooltip>
                    </div>
                    <div class="sort-icon">
                      <v-icon v-if="(hoveredColumnIdx === idx || activeColumnIdx === idx)" small
                              v-on:click="toggleOrder(header, idx)" class="header-btn">
                        {{ sorting.currentSortIcon }}
                      </v-icon>
                    </div>
                  </th>
                </tr>
                <tr v-if="fetchingDataActive" class="datatable__progress">
                  <th class="column" :colspan="columnsCount">
                    <v-progress-linear indeterminate></v-progress-linear>
                  </th>
                </tr>
                </thead>
                <tbody>
                  <template v-for="item in experimentsData" :id="item.attributes.name">
                    <tr v-bind:key="item.attributes.name" >
                      <td>
                        <div class="select-icon">
                          <v-icon v-if="isSelected(item)" color="success" v-on:click="deselectExp(item)" class="pointer-btn"
                                  :disabled="!isTensorboardAvailableForExp(item.attributes.type)">
                            check_circle
                          </v-icon>
                          <v-icon v-if="!isSelected(item)" v-on:click="selectExp(item)" class="pointer-btn"
                                  :disabled="!isTensorboardAvailableForExp(item.attributes.type)">
                            panorama_fish_eye
                          </v-icon>
                        </div>
                      </td>
                      <td v-for="param in experimentsParams" v-bind:key="param" v-if="isVisibleColumn(param)">
                        <span v-if="param === 'name'" id="exp-name" v-on:click="toggleDetails(item.attributes.name)">
                          {{ parseValue(param, item.attributes[param]) || '-' }}
                        </span>
                        <span v-if="param !== 'name'">
                          {{ parseValue(param, item.attributes[param]) || '-' }}
                        </span>
                      </td>
                    </tr>
                    <tr v-if="areDetailsVisible(item.attributes.name)" v-bind:key="item.attributes.name + '_expand'">
                      <th :colspan="columnsCount" class="expanded-view">
                        <div class="exp-details">
                          <v-layout row>
                            <v-flex xs6 wrap>
                              <ExpResourcesDetail :keyname="labels.RESOURCES" :podsList="experimentResources(item.attributes.name)"/>
                              <ExpKeyValDetail :keyname="labels.EXPERIMENT_SUBMISSION_DATE" :value="parseValue('creationTimestamp', item.attributes.creationTimestamp)"/>
                            </v-flex>
                            <v-flex>
                              <div class="vertical-line"></div>
                            </v-flex>
                            <v-flex xs6 wrap>
                              <ExpKeyValDetail :keyname="labels.EXPERIMENT_START_DATE" :value="parseValue('trainingStartTime', item.attributes.trainingStartTime)"/>
                              <ExpKeyValDetail :keyname="labels.TOTAL_EXPERIMENT_DURATION" :value="parseValue('trainingDurationTime', item.attributes.trainingDurationTime)"/>
                              <ExpKeyValDetail :keyname="labels.PARAMETERS" :value="parseValue('parameters', item.attributes.parameters)"/>
                            </v-flex>
                          </v-layout>
                        </div>
                      </th>
                    </tr>
                  </template>
                </tbody>
              </table>
            </div>
            <div id="nodata" v-if="experimentsTotal === 0">
              <v-alert :value="true" type="info">
                {{ messages.SUCCESS.NO_DATA }}
              </v-alert>
            </div>
            <div id="nodata" v-if="filteredDataCount === 0 && experimentsTotal !== 0 && customFiltersActive">
              <v-alert :value="true" type="info">
                {{ messages.SUCCESS.NO_DATA_FOR_FILTER }}
              </v-alert>
            </div>
            <div id="nodata" v-if="filteredDataCount === 0 && experimentsTotal !== 0 && !customFiltersActive">
              <v-alert :value="true" type="info">
                {{ messages.SUCCESS.NO_DATA_FOR_CURRENT_USER }}
                Click <u class="pointer-btn" v-on:click="showAllUsersData()">here</u> to load all users data.
              </v-alert>
            </div>
            <FooterElements v-if="filteredDataCount"
              :currentPage="pagination.currentPage"
              :pagesCount="experimentsTotalPagesCount"
              :nextPageAction="nextPage"
              :prevPageAction="previousPage"
              :paginationStats="paginationStats"
              :updateCountHandler="updateCountPerPage"
              :lastUpdateLabel="refresh.lastUpdateLabel"
            ></FooterElements>
          </div>
        </v-card>
      </v-flex>
    </v-layout>
</template>

<script>
import LABELS from '../utils/header-titles';
import ELEMENT_LABELS from '../utils/constants/labels';
import MESSAGES from '../utils/constants/messages';
import {mapGetters, mapActions} from 'vuex';
import ActionHeaderButtons from './ModelsTableFeatures/ActionHeaderButtons';
import FilterByValWindow from './ModelsTableFeatures/FilterByValWindow';
import ExpKeyValDetail from './ModelsTableFeatures/ExpKeyValDetail';
import ExpResourcesDetail from './ModelsTableFeatures/ExpResourcesDetail';
import FooterElements from './ModelsTableFeatures/FooterElements';
import TimedateExtractor from '../utils/timedate-extractor';

const SORTING_ORDER = {
  ASC: 'asc',
  DESC: 'desc'
};

const DEFAULT_ORDER = {
  key: 0,
  orderBy: 'creationTimestamp',
  order: SORTING_ORDER.DESC,
  sortIcon: 'arrow_downward'
};

export default {
  name: 'ModelsTable',
  components: {
    ActionHeaderButtons,
    ExpKeyValDetail,
    ExpResourcesDetail,
    FilterByValWindow,
    FooterElements
  },
  data: () => {
    return {
      labels: ELEMENT_LABELS,
      messages: MESSAGES,
      filterIcon: 'filter_list',
      tbCompatibleExpKinds: ['training'],
      searchPattern: '',
      selectedByUserColumns: [],
      alwaysVisibleColumns: ['name', 'state', 'creationTimestamp', 'trainingStartTime', 'trainingDurationTime',
        'type'],
      filterableByValColumns: ['name', 'namespace', 'state', 'type'],
      filterByValModals: {
        name: {
          visible: false,
          params: []
        },
        namespace: {
          visible: false,
          params: []
        },
        state: {
          visible: false,
          params: []
        },
        type: {
          visible: false,
          params: []
        }
      },
      sorting: {
        order: DEFAULT_ORDER.order,
        iconAsc: 'arrow_upward',
        iconDesc: 'arrow_downward',
        currentSortIcon: 'arrow_downward'
      },
      pagination: {
        itemsCountPerPage: 5,
        currentPage: 1
      },
      visibleDetails: [],
      activeColumnIdx: DEFAULT_ORDER.key,
      activeColumnName: DEFAULT_ORDER.orderBy,
      hoveredColumnIdx: null,
      selected: [],
      refresh: {
        interval: 30,
        lastUpdateLabel: 'Last updated moment ago.'
      }
    }
  },
  created: function () {
    this.filterByValModals.namespace.params.push(this.username);
    const refreshMode = false;
    this.getData(refreshMode);
    const this2 = this;
    this.intervalId = setInterval(this.timer, 1000, this2);
  },
  beforeDestroy: function () {
    clearInterval(this.intervalId);
  },
  computed: {
    ...mapGetters({
      experimentsData: 'experimentsData',
      experimentsParams: 'experimentsParams',
      columnValuesOptions: 'columnValuesOptions',
      columnValuesApplied: 'columnValuesApplied',
      experimentsBegin: 'experimentsBegin',
      experimentsTotal: 'experimentsTotal',
      filteredDataCount: 'filteredDataCount',
      experimentsEnd: 'experimentsEnd',
      experimentsPageNumber: 'experimentsPageNumber',
      experimentsTotalPagesCount: 'experimentsTotalPagesCount',
      lastUpdate: 'lastUpdate',
      fetchingDataActive: 'fetchingDataActive',
      tensorboardLaunching: 'tensorboardLaunching',
      isCheckingAuth: 'authLoadingState',
      isInitializedData: 'initializedDataFlag',
      isLogged: 'isLogged',
      username: 'username',
      experimentResources: 'experimentResources'
    }),
    paginationStats: function () {
      return `${this.experimentsBegin}-${this.experimentsEnd} ${this.labels.OF} ${this.filteredDataCount}`;
    },
    currentlyVisibleColumns: function () {
      return this.experimentsParams.filter((header) => {
        if (this.alwaysVisibleColumns.includes(header) || this.selectedByUserColumns.includes(header)) {
          return header;
        }
      });
    },
    customizableVisibilityColumns: function () {
      return this.experimentsParams.filter((header) => {
        if (!this.alwaysVisibleColumns.includes(header)) {
          return header;
        }
      }).sort();
    },
    refreshTableDataTriggers: function () {
      return `${this.searchPattern}|${this.sorting.order}|${this.activeColumnName}|${this.pagination.itemsCountPerPage}|
      ${this.pagination.currentPage}|${JSON.stringify(this.filterByValModals)}`;
    },
    tensorBtnAvailable: function () {
      return this.selected.length > 0;
    },
    columnsCount: function () {
      return this.currentlyVisibleColumns.length > 6 ? 8 : this.currentlyVisibleColumns.length + 1;
    },
    customFiltersActive: function () {
      return this.filterByValModals.state.params.length || this.filterByValModals.name.params.length ||
        this.filterByValModals.type.params.length || this.filterByValModals.namespace.params.length > 1 ||
        this.searchPattern !== '';
    },
    filterByValWindowVisible: function () {
      return Object.keys(this.filterByValModals).map((item) => {
        return this.filterByValModals[item].visible;
      }).reduce((previous, current) => {
        return previous || current;
      });
    }
  },
  watch: {
    refreshTableDataTriggers: function () {
      const refreshMode = false;
      this.getData(refreshMode);
    },
    experimentsPageNumber: function () {
      this.pagination.currentPage = this.experimentsPageNumber;
    }
  },
  methods: {
    ...mapActions(['getUserExperiments', 'getExperimentResources', 'launchTensorboard']),
    getLabel: function (header) {
      return LABELS[header] || header.charAt(0).toUpperCase() + header.slice(1);
    },
    toggleOrder (column, idx) {
      this.activeColumnIdx = idx;
      this.activeColumnName = column;
      this.sorting.order = this.sorting.order === SORTING_ORDER.ASC ? SORTING_ORDER.DESC : SORTING_ORDER.ASC;
      this.sorting.currentSortIcon = this.sorting.order === SORTING_ORDER.ASC ? this.sorting.iconAsc : this.sorting.iconDesc;
    },
    clearSort () {
      this.activeColumnName = DEFAULT_ORDER.orderBy;
      this.activeColumnIdx = DEFAULT_ORDER.key;
      this.sorting.order = DEFAULT_ORDER.order;
      this.sorting.currentSortIcon = DEFAULT_ORDER.sortIcon;
    },
    clearFilter () {
      Object.keys(this.filterByValModals).forEach((item) => {
        this.filterByValModals[item].params = [];
      });
      this.filterByValModals.namespace.params.push(this.username);
      this.searchPattern = '';
    },
    showAllUsersData () {
      this.filterByValModals.namespace.params = [];
    },
    updateCountPerPage (count) {
      this.pagination.itemsCountPerPage = count;
      this.pagination.currentPage = 1;
    },
    nextPage () {
      this.pagination.currentPage++;
    },
    previousPage () {
      this.pagination.currentPage--;
    },
    isVisibleColumn (column) {
      return this.currentlyVisibleColumns.includes(column);
    },
    isFilterableByValColumn (column) {
      return this.filterableByValColumns.includes(column);
    },
    setVisibleColumns (columns) {
      this.selectedByUserColumns = this.alwaysVisibleColumns.concat(columns);
    },
    onLaunchTensorboardClick () {
      const experiments = this.selected.map((exp) => {
        return `${exp.attributes.namespace}=${encodeURIComponent(exp.attributes.name)}`;
      }).join('&');
      window.open(`/tensorboard?${experiments}`);
      this.selected = [];
    },
    toggleDetails (expName) {
      if (this.areDetailsVisible(expName)) {
        this.visibleDetails = this.visibleDetails.filter((exp) => {
          return exp !== expName;
        })
      } else {
        this.getExperimentResources({experimentName: expName})
          .then(() => {
            this.visibleDetails.push(expName);
          });
      }
    },
    areDetailsVisible (expName) {
      return this.visibleDetails.includes(expName);
    },
    selectExp (exp) {
      this.selected.push(exp);
    },
    deselectExp (exp) {
      this.selected = this.selected.filter((item) => {
        return item.attributes.name !== exp.attributes.name;
      });
    },
    isSelected (exp) {
      const filtered = this.selected.filter((item) => {
        return item.attributes.name === exp.attributes.name;
      });
      return filtered.length !== 0;
    },
    getData (refreshMode) {
      this.getUserExperiments({
        limitPerPage: this.pagination.itemsCountPerPage,
        pageNo: this.pagination.currentPage,
        orderBy: this.activeColumnName,
        order: this.sorting.order,
        searchBy: this.searchPattern,
        names: this.filterByValModals.name.params,
        namespaces: this.filterByValModals.namespace.params,
        states: this.filterByValModals.state.params,
        types: this.filterByValModals.type.params,
        refreshMode: refreshMode
      });
      this.visibleDetails.forEach((item) => {
        this.getExperimentResources({experimentName: item})
      });
    },
    timer (context) {
      const currentTime = Date.now();
      const lastUpdateTimeDiffer = Math.ceil((currentTime - this.lastUpdate) / 1000); // in seconds
      if (lastUpdateTimeDiffer <= this.refresh.interval) {
        this.refresh.lastUpdateLabel = context.messages.SUCCESS.LAST_UPDATED_A_MOMENT_AGO;
      } else {
        this.refresh.lastUpdateLabel = context.messages.SUCCESS.LAST_UPDATED_30S_AGO;
        if (!this.fetchingDataActive) {
          const refreshMode = true;
          this.getData(refreshMode);
        }
      }
    },
    parseValue (key, arg1) {
      switch (key) {
        case 'creationTimestamp':
          return new Date(arg1).toLocaleString();
        case 'trainingStartTime':
        case 'trainingEndTime':
          return arg1 ? new Date(arg1).toLocaleString() : '---';
        case 'trainingDurationTime':
          const duration = new Date(arg1);
          const pData = TimedateExtractor(duration);
          return `${pData.days} days, ${pData.hours} hrs, ${pData.minutes} mins, ${pData.seconds} s`;
        case 'type':
          return arg1 ? arg1.charAt(0).toUpperCase() + arg1.slice(1) : '-';
        case 'parameters':
          if (!arg1) {
            return '--';
          }
          return Array.isArray(arg1) ? arg1.join(', ') : arg1;
        default:
          return arg1;
      }
    },
    switchFilterWindow (column, visible) {
      Object.keys(this.filterByValModals).forEach((column) => {
        this.filterByValModals[column].visible = false;
      });
      this.filterByValModals[column].visible = visible;
    },
    onApplyValuesColumnFilter (column, draft) {
      this.switchFilterWindow(column, false);
      this.filterByValModals[column].params = [].concat(draft);
    },
    isTensorboardAvailableForExp (expType) {
      return this.tbCompatibleExpKinds.includes(expType);
    }
  }
}
</script>

<style scoped>
.filter-icon {
  width: 25px;
  float: left;
  padding-right: 5px;
}
.cell-title {
  max-width: 100px;
  float: left;
  text-overflow: ellipsis;
  overflow: hidden;
  padding-right: 5px;
  text-align: left;
}
.sort-icon {
  width: 30px;
  float: right;
  padding-left: 5px;
  padding-right: 5px;
}
.overflow {
  width: 100%;
  display: block;
  overflow: scroll;
  overflow-scrolling: auto;
  max-height: 500px;
}
.static-height {
  height: 500px !important;
}
.table-style table {
  table-layout: fixed;
}
.table-style th {
  height: 46px;
  color: rgba(0, 0, 0, 0.52);
}
.overflow thead th {
  position: sticky;
  top: 0px;
  z-index: 1;
}
.table-style th {
  background-color: #f2f2f2;
  border-right: 1px solid #ffffff;
}
.table-style th:first-child {
  background-color: #ffffff;
}
.table-style tr:nth-child(even) {
  background-color: #f2f2f2;
}
.table-style td {
  font-size: 12px;
}
.select-icon {
  width: 24px;
}
.pointer-btn {
  cursor: pointer;
}
.active {
  font-weight: bold;
}
#nodata {
  height: 80px;
}
#exp-name {
  font-weight: bold;
  text-decoration: underline;
  cursor: pointer;
}
.expanded-view {
  color: rgba(0, 0, 0, 0.87) !important;
  font-weight: normal;
  text-align: left;
}
.exp-details {
  margin: 20px 20px 20px 45px;
}
.vertical-line {
  border-left: 1px dashed rgba(0, 0, 0, 0.87);
  height: 100%;
  margin-right: 20px;
  margin-left: 20px;
}
.elevation {
  -webkit-box-shadow: -30px 28px 43px -30px rgba(0,0,0,0.2);
  -moz-box-shadow: -30px 28px 43px -30px rgba(0,0,0,0.2);
  box-shadow: -30px 28px 43px -30px rgba(0,0,0,0.2);
}
</style>
