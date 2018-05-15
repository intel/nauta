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
      <v-flex xs12 md4 offset-md8>
        <v-card-title>
          <v-text-field append-icon="search" single-line hide-details v-model="searchPattern"></v-text-field>
        </v-card-title>
      </v-flex>
      <v-flex xs12>
        <v-card>
          <v-card-title>
            <h2>Models</h2>
            <v-spacer></v-spacer>
            <ActionHeaderButtons
              :clearSort="clearSort" :hiddenColumns="hiddenColumns" :setHiddenColumnsHandler="setHiddenColumns" :headers="headers"
            ></ActionHeaderButtons>
          </v-card-title>
          <div class="elevation-3">
            <div class="table__overflow">
              <table class="datatable table">
                <thead>
                <th class="text-xs-left">
                  <v-icon small class="pointer-btn">{{ filterIcon }}</v-icon>
                  Favourites
                </th>
                <th v-for="(header, idx) in headers" v-if="isVisibleColumn(header.value)" v-bind:key="header.value" class="text-xs-left"
                    @mouseover="hoveredColumnIdx = idx" @mouseleave="hoveredColumnIdx = null">
                  <v-icon v-if="header.filterable" small class="pointer-btn">{{ filterIcon }}</v-icon>
                  <v-tooltip bottom>
                    <span slot="activator" v-bind:class="{active: activeColumnName === header.value}">
                      {{ cutLongText(header.text) }}
                    </span>
                    <span>{{ header.text }}</span>
                  </v-tooltip>
                  <v-icon v-if="header.sortable && (hoveredColumnIdx === idx || activeColumnIdx === idx)" small
                          v-on:click="toggleOrder(header.value, idx)" class="header-btn">
                    {{ sorting.currentSortIcon }}
                  </v-icon>
                </th>
                </thead>
                <tbody>
                <tr v-for="item in orderedData" v-bind:key="item.modelName">
                  <td>
                    <v-icon class="pointer-btn">star_border</v-icon>
                  </td>
                  <td v-for="attr in Object.keys(item)" v-bind:key="attr" v-if="isVisibleColumn(attr)">
                    {{ item[attr] }}
                  </td>
                </tr>
                </tbody>
              </table>
            </div>
            <FooterElements
              :currentPage="pagination.currentPage"
              :pagesCount="pagesCount"
              :nextPageAction="nextPage"
              :prevPageAction="previousPage"
              :paginationStats="paginationStats"
              :updateCountHandler="updateCountPerPage"
            ></FooterElements>
          </div>
        </v-card>
      </v-flex>
    </v-layout>
</template>

<script>
import lodash from 'lodash';
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
      searchPattern: '',
      hiddenColumns: [],
      sorting: {
        order: SORTING_ORDER.ASC,
        iconAsc: 'arrow_upward',
        iconDesc: 'arrow_downward',
        currentSortIcon: 'arrow_upward'
      },
      pagination: {
        currentItemsCountPerPage: 5,
        currentPage: 1
      },
      activeColumnIdx: 0,
      activeColumnName: null,
      hoveredColumnIdx: null
    }
  },
  props: {
    headers: Array,
    tableData: Array,
    filterIcon: String,
    lastUpdate: Number
  },
  computed: {
    orderedData: function () {
      // sorting
      const sortedData = lodash.orderBy(this.tableData, [this.activeColumnName], [this.sorting.order]);
      // filtering
      const filteredData = lodash.filter(sortedData, (item) => {
        if (item.modelName.toUpperCase().indexOf(this.searchPattern.toUpperCase()) !== -1 ||
          item.trainingStatus.toUpperCase().indexOf(this.searchPattern.toUpperCase()) !== -1 ||
          item.owner.toUpperCase().indexOf(this.searchPattern.toUpperCase()) !== -1) {
          return item;
        }
      });
      // pagination
      const a = (this.pagination.currentPage - 1) * this.pagination.currentItemsCountPerPage;
      const b = this.pagination.currentPage * this.pagination.currentItemsCountPerPage;
      return filteredData.slice(a, b);
    },
    dataLifeInSeconds: function () {
      return Math.round((Date.now() - this.lastUpdate) / 1000)
    },
    dataItemsCount: function () {
      return this.orderedData.length;
    },
    pagesCount: function () {
      return Math.ceil(this.tableData.length / this.pagination.currentItemsCountPerPage);
    },
    paginationStats: function () {
      const total = this.tableData.length;
      const a = (this.pagination.currentPage - 1) * this.pagination.currentItemsCountPerPage + 1;
      let b = this.pagination.currentPage * this.pagination.currentItemsCountPerPage;
      if (b > total) {
        b = total;
      }
      return `${a}-${b} of ${total}`
    },
    visibleColumns: function () {
      return this.headers.map((header) => {
        if (this.hiddenColumns.indexOf(header.value) === -1) {
          return header.value;
        }
      });
    }
  },
  methods: {
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
    },
    clearFilter () {
      console.log('clear filter');
    },
    revertOrder () {
      console.log('revert order');
    },
    updateCountPerPage (count) {
      this.pagination.currentItemsCountPerPage = count;
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
    }
  }
}
</script>

<style scoped>
th {
  height: 46px;
  color: rgba(0, 0, 0, 0.52);
}
.pointer-btn {
  cursor: pointer;
}
.active {
  font-weight: bold;
}
</style>
