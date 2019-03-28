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
              :onLaunchTensorHandler="onLaunchTensorboardClick"
              :clearSort="clearSort"
              :clearFilterHandler="clearFilter"
              :refreshNowHandler="getData"
            ></ActionHeaderButtons>
            <v-flex v-if="(experimentsTotal !== 0 || searchPattern)" xs12 md2>
              <v-card-title>
                <v-text-field append-icon="search" single-line hide-details v-model="searchPattern"></v-text-field>
              </v-card-title>
            </v-flex>
          </v-card-title>
          <div class="elevation">
            <div v-bind:class="{overflow: filteredDataCount !== 0, 'table-style': true, 'static-height': filterByValWindowVisible }">
              <table v-if="experimentsParams.length !== 0" class="datatable table">
                <thead>
                <tr>
                  <th width="150px">
                    <div>{{ labels.TENSORBOARD_ELIGIBILITY }}</div>
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
                        <v-icon v-if="param === 'name' && areDetailsVisible(item.attributes.name)"
                                class="pointer-btn exp-icon" v-on:click="toggleDetails(item.attributes.name)">
                          keyboard_arrow_down
                        </v-icon>
                        <v-icon v-if="param === 'name' && !areDetailsVisible(item.attributes.name)"
                                class="pointer-btn exp-icon" v-on:click="toggleDetails(item.attributes.name)">
                          keyboard_arrow_up
                        </v-icon>
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
                              <ExpKeyValDetail :keyname="labels.EXPERIMENT_END_DATE" :value="parseValue('trainingEndTime', item.attributes.trainingEndTime)"/>
                              <ExpKeyValDetail :keyname="labels.TOTAL_EXPERIMENT_DURATION" :value="parseValue('trainingDurationTime', item.attributes.trainingDurationTime)"/>
                              <ExpKeyValDetail :keyname="labels.PARAMETERS" :value="parseValue('parameters', item.attributes.parameters)"/>
                              <LogsDetail :keyname="labels.OUTPUT" :owner="item.attributes.namespace" :name="item.attributes.name"/>
                            </v-flex>
                          </v-layout>
                        </div>
                      </th>
                    </tr>
                  </template>
                </tbody>
              </table>
            </div>
            <div v-if="filteredDataCount === 0" id="nodata">
              <v-alert v-if="experimentsTotal === 0" :value="true" type="info">
                {{ messages.SUCCESS.NO_DATA }}
              </v-alert>
              <v-alert v-if="filteredDataCount === 0 && experimentsTotal !== 0 && customFiltersActive" :value="true" type="info">
                {{ messages.SUCCESS.NO_DATA_FOR_FILTER }}
              </v-alert>
              <v-alert v-if="filteredDataCount === 0 && experimentsTotal !== 0 && !customFiltersActive" :value="true" type="info">
                {{ messages.SUCCESS.NO_DATA_FOR_CURRENT_USER }}
                Click <u class="pointer-btn" v-on:click="showAllUsersData()">here</u> to load all users data.
              </v-alert>
            </div>
            <FooterElements v-if="filteredDataCount"/>
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
import LogsDetail from './ModelsTableFeatures/LogsDetail';
import ExpResourcesDetail from './ModelsTableFeatures/ExpResourcesDetail';
import FooterElements from './ModelsTableFeatures/FooterElements';
import {TimedateExtractor, toLocaleFormat} from '../utils/timedate-utils';
import {FILTERABLE_BY_VAL_COLUMNS} from '../store/modules/experiments-table';

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
    LogsDetail,
    FooterElements
  },
  data: () => {
    return {
      labels: ELEMENT_LABELS,
      messages: MESSAGES,
      filterIcon: 'filter_list',
      tbCompatibleExpKinds: ['training'],
      searchPattern: '',
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
      visibleDetails: [],
      activeColumnIdx: DEFAULT_ORDER.key,
      activeColumnName: DEFAULT_ORDER.orderBy,
      hoveredColumnIdx: null
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
      selectedExperimentsByUser: 'selectedExperimentsByUser',
      experimentsParams: 'experimentsParams',
      currentlyVisibleColumns: 'currentlyVisibleColumns',
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
      experimentResources: 'experimentResources',
      itemsCountPerPage: 'itemsCountPerPage',
      currentPage: 'currentPage',
      refreshInterval: 'refreshInterval',
      allUsersMode: 'allUsersMode'
    }),
    refreshTableDataTriggers: function () {
      return `${this.searchPattern}|${this.sorting.order}|${this.activeColumnName}|${this.itemsCountPerPage}|
      ${this.currentPage}|${JSON.stringify(this.filterByValModals)}|${this.allUsersMode}`;
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
    }
  },
  methods: {
    ...mapActions([
      'getUserExperiments',
      'getExperimentResources',
      'launchTensorboard',
      'clearExperimentSelection',
      'markExperimentsAsSelected',
      'markExperimentAsSelected',
      'showColumns',
      'showColumn',
      'showRefreshMessage',
      'clearAllUsersMode'
    ]),
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
      this.clearAllUsersMode();
    },
    showAllUsersData () {
      this.filterByValModals.namespace.params = [];
    },
    isVisibleColumn (column) {
      return this.currentlyVisibleColumns.includes(column);
    },
    isFilterableByValColumn (column) {
      return FILTERABLE_BY_VAL_COLUMNS.includes(column);
    },
    setVisibleColumns (columns) {
      this.showColumns({data: columns});
    },
    onLaunchTensorboardClick () {
      const experiments = this.selectedExperimentsByUser.map((exp) => {
        return `${exp.attributes.namespace}=${encodeURIComponent(exp.attributes.name)}`;
      }).join('&');
      window.open(`/tensorboard?${experiments}`);
      this.clearExperimentSelection();
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
      this.markExperimentAsSelected({data: [exp]})
    },
    deselectExp (exp) {
      const filteredExperiments = this.selectedExperimentsByUser.filter((item) => {
        return item.attributes.name !== exp.attributes.name;
      });
      this.markExperimentsAsSelected({ data: filteredExperiments });
    },
    isSelected (exp) {
      const filtered = this.selectedExperimentsByUser.filter((item) => {
        return item.attributes.name === exp.attributes.name;
      });
      return filtered.length !== 0;
    },
    getData (refreshMode) {
      this.getUserExperiments({
        limitPerPage: this.itemsCountPerPage,
        pageNo: this.currentPage,
        orderBy: this.activeColumnName,
        order: this.sorting.order,
        searchBy: this.searchPattern,
        names: this.filterByValModals.name.params,
        namespaces: this.allUsersMode ? [] : this.filterByValModals.namespace.params,
        states: this.filterByValModals.state.params,
        types: this.filterByValModals.type.params,
        refreshMode: refreshMode
      });
      this.visibleDetails.forEach((item) => {
        this.getExperimentResources({experimentName: item})
      });
    },
    timer (context) {
      this.showRefreshMessage({data: context.messages.SUCCESS.LAST_UPDATED_ON(this.lastUpdate)});
      const currentTime = Date.now();
      const lastUpdateTimeDiffer = Math.ceil((currentTime - this.lastUpdate) / 1000); // in seconds
      if (lastUpdateTimeDiffer >= this.refreshInterval) {
        if (!this.fetchingDataActive) {
          const refreshMode = true;
          this.getData(refreshMode);
        }
      }
    },
    parseValue (key, arg1) {
      switch (key) {
        case 'creationTimestamp':
          return toLocaleFormat(arg1);
        case 'trainingStartTime':
        case 'trainingEndTime':
          return arg1 ? toLocaleFormat(arg1) : '---';
        case 'trainingDurationTime':
        case 'trainingTimeInQueue':
          if (arg1 === 0) {
            return '---';
          }
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
.exp-icon {
  float: left;
  width: 25px;
  padding-right: 5px;
  margin-top: -3px;
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
.table-style tr:nth-child(even) {
  background-color: #f2f2f2;
}
.table-style td {
  font-size: 12px;
}
.select-icon {
  margin-left: auto;
  margin-right: auto;
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
