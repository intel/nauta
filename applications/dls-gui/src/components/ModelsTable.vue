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
      <v-flex xs12>
        <v-card>
          <v-card-title>
            <h2>Models</h2>
            <v-spacer></v-spacer>
            <ActionHeaderButtons v-if="experimentsTotal !== 0"
              :clearSort="clearSort"
              :hiddenColumns="hiddenColumns"
              :setHiddenColumnsHandler="setHiddenColumns"
              :onLaunchTensorHandler="launchTensorboard"
              :onDiscardTensorHandler="discardTensorboard"
              :headers="experimentsParams"
            ></ActionHeaderButtons>
            <v-flex xs12 md3 v-if="!tensorMode && (experimentsTotal !== 0 || searchPattern)">
              <v-card-title>
                <v-text-field append-icon="search" single-line hide-details v-model="searchPattern"></v-text-field>
              </v-card-title>
            </v-flex>
          </v-card-title>
          <v-alert v-if="experimentsTotal === 0" :value="true" type="info">
            No data to display.
          </v-alert>
          <div class="elevation-3">
            <div class="table__overflow">
              <table class="datatable table">
                <thead>
                  <th v-if="tensorMode"></th>
                  <th v-for="(header, idx) in experimentsParams" v-if="isVisibleColumn(header)" :id="header" v-bind:key="header"
                      class="text-xs-left" @mouseover="hoveredColumnIdx = idx" @mouseleave="hoveredColumnIdx = null">
                    <v-icon small class="pointer-btn">{{ filterIcon }}</v-icon>
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
                  <td v-for="attr in Object.keys(item)" v-bind:key="attr" v-if="isVisibleColumn(attr)">
                    {{ item[attr] }}
                  </td>
                </tr>
                </tbody>
              </table>
            </div>
            <FooterElements v-if="experimentsTotal"
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
import FooterElements from './ModelsTableFeatures/FooterElements';

const SORTING_ORDER = {
  ASC: 'asc',
  DESC: 'desc'
};

export default {
  name: 'ModelsTable',
  components: {
    ActionHeaderButtons,
    FooterElements
  },
  data: () => {
    return {
      filterIcon: 'filter_list',
      searchPattern: '',
      hiddenColumns: [],
      sorting: {
        order: SORTING_ORDER.ASC,
        iconAsc: 'arrow_upward',
        iconDesc: 'arrow_downward',
        currentSortIcon: 'arrow_upward'
      },
      pagination: {
        itemsCountPerPage: 5,
        currentPage: 1
      },
      activeColumnIdx: 0,
      activeColumnName: null,
      hoveredColumnIdx: null,
      selected: [],
      refresh: {
        interval: 30,
        lastUpdateLabel: 'Last updated moment ago.'
      }
    }
  },
  created: function () {
    this.getData();
    this.intervalId = setInterval(this.timer, 1000);
  },
  beforeDestroy: function () {
    clearInterval(this.intervalId);
  },
  computed: {
    ...mapGetters({
      experimentsData: 'experimentsData',
      experimentsParams: 'experimentsParams',
      experimentsBegin: 'experimentsBegin',
      experimentsTotal: 'experimentsTotal',
      experimentsEnd: 'experimentsEnd',
      experimentsPageNumber: 'experimentsPageNumber',
      experimentsTotalPagesCount: 'experimentsTotalPagesCount',
      lastUpdate: 'lastUpdate',
      fetchingDataActive: 'fetchingDataActive',
      tensorMode: 'tensorMode'
    }),
    paginationStats: function () {
      return `${this.experimentsBegin}-${this.experimentsEnd} of ${this.experimentsTotal}`;
    },
    visibleColumns: function () {
      return this.experimentsParams.map((header) => {
        if (this.hiddenColumns.indexOf(header) === -1) {
          return header;
        }
      });
    },
    refreshTableDataTriggers: function () {
      return `${this.searchPattern}|${this.sorting.order}|${this.activeColumnName}|${this.pagination.itemsCountPerPage}|
      ${this.pagination.currentPage}`;
    }
  },
  watch: {
    refreshTableDataTriggers: function () {
      this.getData();
    },
    experimentsPageNumber: function () {
      this.pagination.currentPage = this.experimentsPageNumber;
    }
  },
  methods: {
    ...mapActions(['getUserExperiments', 'enableTensorMode', 'disableTensorMode']),
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
      this.activeColumnName = null;
      this.activeColumnIdx = null;
      this.sorting.order = '';
    },
    clearFilter () {
      console.log('clear filter');
    },
    revertOrder () {
      console.log('revert order');
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
      return this.visibleColumns.indexOf(column) !== -1;
    },
    setHiddenColumns (columns) {
      this.hiddenColumns = columns;
    },
    launchTensorboard () {
      if (this.tensorMode) {
        alert('Now tensorboard should be run with params: ' + JSON.stringify(this.selected));
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
    getData () {
      this.getUserExperiments({
        limitPerPage: this.pagination.itemsCountPerPage,
        pageNo: this.pagination.currentPage,
        orderBy: this.activeColumnName,
        order: this.sorting.order,
        searchBy: this.searchPattern
      });
    },
    timer () {
      const currentTime = Date.now();
      const lastUpdateTimeDiffer = Math.ceil((currentTime - this.lastUpdate) / 1000); // in seconds
      if (lastUpdateTimeDiffer <= this.refresh.interval) {
        this.refresh.lastUpdateLabel = 'Last updated moment ago.';
      } else {
        this.refresh.lastUpdateLabel = `Last updated over ${this.refresh.interval} seconds ago.`;
        if (!this.fetchingDataActive) {
          this.getData();
        }
      }
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
