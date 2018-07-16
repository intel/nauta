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
        <v-progress-circular :size="90" indeterminate color="warning">Loading...</v-progress-circular>
      </v-container>
      <v-flex v-if="isLogged && isInitializedData && !tensorboardLaunching" xs12>
        <v-card>
          <v-card-title>
            <h2>Models</h2>
            <v-spacer></v-spacer>
            <ActionHeaderButtons v-if="experimentsTotal !== 0"
              :clearSort="clearSort"
              :clearFilterHandler="clearFilter"
              :hiddenColumns="hiddenColumns"
              :alwaysVisibleColumns="alwaysVisibleColumns"
              :setHiddenColumnsHandler="setHiddenColumns"
              :onLaunchTensorHandler="onLaunchTensorboardClick"
              :launchTensorDisabled="!tensorBtnAvailable"
              :onDiscardTensorHandler="discardTensorboard"
              :headers="experimentsParams"
            ></ActionHeaderButtons>
            <v-flex xs12 md3 v-if="!tensorMode && (experimentsTotal !== 0 || searchPattern)">
              <v-card-title>
                <v-text-field append-icon="search" single-line hide-details v-model="searchPattern"></v-text-field>
              </v-card-title>
            </v-flex>
          </v-card-title>
          <v-alert v-if="filteredDataCount === 0" :value="true" type="info">
            No data to display.
          </v-alert>
          <div class="elevation-3">
            <div class="table__overflow">
              <table class="datatable table">
                <thead>
                <tr>
                  <th v-if="tensorMode"></th>
                  <th v-for="(header, idx) in experimentsParams" v-if="isVisibleColumn(header)" :id="header" v-bind:key="header"
                      class="text-xs-left" @mouseover="hoveredColumnIdx = idx" @mouseleave="hoveredColumnIdx = null">
                    <v-icon v-if="isFilterableByValColumn(header)" v-on:click="switchFilterWindow(header, true)" small class="pointer-btn">{{ filterIcon }}</v-icon>
                    <FilterByValWindow v-if="filterByValModals[header] && filterByValModals[header].visible"
                                       :column-name="header"
                                       :options="columnValuesOptions[header]"
                                       :onCloseClickHandler="switchFilterWindow"
                                       :onApplyClickHandler="onApplyValuesColumnFilter"
                                       :appliedOptions="columnValuesApplied[header]"
                    >
                    </FilterByValWindow>
                    <v-tooltip bottom>
                      <span slot="activator" v-bind:class="{active: activeColumnName === header}">
                        {{ cutLongText(getLabel(header)) }}
                      </span>
                      <span>{{ getLabel(header) }}</span>
                    </v-tooltip>
                    <v-icon v-if="(hoveredColumnIdx === idx || activeColumnIdx === idx)" small
                            v-on:click="toggleOrder(header, idx)" class="header-btn">
                      {{ sorting.currentSortIcon }}
                    </v-icon>
                  </th>
                </tr>
                <tr v-if="fetchingDataActive" class="datatable__progress">
                  <th class="column" colspan="1000">
                    <v-progress-linear indeterminate></v-progress-linear>
                  </th>
                </tr>
                </thead>
                <tbody>
                <tr v-for="item in experimentsData" v-bind:key="item.name" :id="item.name">
                  <td v-if="tensorMode">
                    <v-icon v-if="isSelected(item)" color="success" v-on:click="deselectExp(item)" class="pointer-btn">
                      check_circle
                    </v-icon>
                    <v-icon v-if="!isSelected(item)" v-on:click="selectExp(item)" class="pointer-btn">
                      panorama_fish_eye
                    </v-icon>
                  </td>
                  <td v-for="param in experimentsParams" v-bind:key="param" v-if="isVisibleColumn(param)">
                    {{ parseValue(param, item[param]) || '-' }}
                  </td>
                </tr>
                </tbody>
              </table>
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
import {mapGetters, mapActions} from 'vuex';
import ActionHeaderButtons from './ModelsTableFeatures/ActionHeaderButtons';
import FilterByValWindow from './ModelsTableFeatures/FilterByValWindow';
import FooterElements from './ModelsTableFeatures/FooterElements';

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
    FilterByValWindow,
    FooterElements
  },
  data: () => {
    return {
      filterIcon: 'filter_list',
      searchPattern: '',
      hiddenColumns: [],
      alwaysVisibleColumns: ['creationTimestamp', 'namespace', 'name', 'state'],
      filterableByValColumns: ['name', 'namespace', 'state'],
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
    const refreshMode = false;
    this.getData(refreshMode);
    this.intervalId = setInterval(this.timer, 1000);
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
      tensorMode: 'tensorMode',
      isCheckingAuth: 'authLoadingState',
      isInitializedData: 'initializedDataFlag',
      isLogged: 'isLogged'
    }),
    paginationStats: function () {
      return `${this.experimentsBegin}-${this.experimentsEnd} of ${this.filteredDataCount}`;
    },
    visibleColumns: function () {
      return this.experimentsParams.map((header) => {
        if (!this.hiddenColumns.includes(header)) {
          return header;
        }
      });
    },
    refreshTableDataTriggers: function () {
      return `${this.searchPattern}|${this.sorting.order}|${this.activeColumnName}|${this.pagination.itemsCountPerPage}|
      ${this.pagination.currentPage}|${JSON.stringify(this.filterByValModals)}`;
    },
    tensorBtnAvailable: function () {
      return !this.tensorMode || (this.tensorMode && this.selected.length > 0);
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
    ...mapActions(['getUserExperiments', 'enableTensorMode', 'disableTensorMode', 'launchTensorboard']),
    getLabel: function (header) {
      return LABELS[header] || header;
    },
    cutLongText (str) {
      return str.length > 14 ? `${str.substr(0, 14)}...` : str;
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
      this.searchPattern = '';
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
      return this.visibleColumns.includes(column);
    },
    isFilterableByValColumn (column) {
      return this.filterableByValColumns.includes(column);
    },
    setHiddenColumns (columns) {
      this.hiddenColumns = columns;
    },
    onLaunchTensorboardClick () {
      if (this.tensorMode) {
        const experiments = this.selected.map((exp) => {
          return `${exp.namespace}=${encodeURIComponent(exp.name)}`;
        }).join('&');
        window.open(`/tensorboard?${experiments}`);
        this.discardTensorboard();
      } else {
        this.enableTensorMode();
      }
    },
    discardTensorboard () {
      this.disableTensorMode();
      this.selected = [];
    },
    selectExp (exp) {
      this.selected.push(exp);
    },
    deselectExp (exp) {
      this.selected = this.selected.filter((item) => {
        return item.name !== exp.name;
      });
    },
    isSelected (exp) {
      const filtered = this.selected.filter((item) => {
        return item.name === exp.name;
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
        refreshMode: refreshMode
      });
    },
    timer () {
      const currentTime = Date.now();
      const lastUpdateTimeDiffer = Math.ceil((currentTime - this.lastUpdate) / 1000); // in seconds
      if (lastUpdateTimeDiffer <= this.refresh.interval) {
        this.refresh.lastUpdateLabel = 'Last updated a moment ago.';
      } else {
        this.refresh.lastUpdateLabel = `Last updated over ${this.refresh.interval} seconds ago.`;
        if (!this.fetchingDataActive) {
          const refreshMode = true;
          this.getData(refreshMode);
        }
      }
    },
    parseValue (key, value) {
      switch (key) {
        case 'creationTimestamp':
          return new Date(value).toLocaleString();
        default:
          return value;
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
    }
  }
}
</script>

<style scoped>
th {
  height: 46px;
  color: rgba(0, 0, 0, 0.52);
  font-size: 14px !important;
}
.pointer-btn {
  cursor: pointer;
}
.active {
  font-weight: bold;
}
</style>
