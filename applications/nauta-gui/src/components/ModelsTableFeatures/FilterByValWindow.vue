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
  <div class="filter-box elevation-3">
    <v-container>
      <h4>{{ labels.FILTER_BY_VAL }}...</h4>
      <v-layout row wrap>
        <v-flex xs12>
          <v-btn color="intel_primary" small flat v-on:click="selectAll()">
            {{ labels.SELECT_ALL }}
          </v-btn>
          <v-btn color="intel_primary" small flat v-on:click="deselectAll()">
            {{ labels.CLEAR_ALL }}
          </v-btn>
        </v-flex>
        <v-flex xs12>
          <v-text-field v-model="searchPattern" append-icon="search" box hide-details></v-text-field>
        </v-flex>
        <v-flex xs12>
          <div id="options" class="scroll-y">
            <div v-for="option in boxOptions" v-bind:key="option"
                 class="input-group--selection-controls" v-on:click="switchOption(option)">
              <v-icon :id="option" class="pointer-btn" :color="isSelected(option) ? 'success' : 'grey lighten-3'">
                done
              </v-icon>
              <v-tooltip bottom>
                <span slot="activator" class="label-box">
                  {{ cutLongText(option) }}
                </span>
                <span>{{ option }}</span>
              </v-tooltip>
            </div>
            <div id="load-more">
              <v-btn color="intel_primary" small flat v-if="loadMoreBtnVisibility" v-on:click="onLoadMoreAction()">
                {{ labels.LOAD_MORE }}...
              </v-btn>
            </div>
          </div>
        </v-flex>
        <v-flex xs12 pl-3>
          <v-btn dark small color="intel_primary" v-on:click="onCloseAction()">
            {{ labels.CANCEL }}
          </v-btn>
          <v-btn dark small color="intel_primary" v-on:click="onApplyAction()">
            {{ labels.OK }}
          </v-btn>
        </v-flex>
      </v-layout>
    </v-container>
  </div>
</template>

<script>
import ELEMENT_LABELS from '../../utils/constants/labels';

const DEFAULT_PAGINATION_LIMIT = 10;

export default {
  name: 'FilterByValWindow',
  props: ['columnName', 'options', 'appliedOptions', 'onCloseClickHandler', 'onApplyClickHandler'],
  data: () => {
    return {
      searchPattern: '',
      chosenOptions: [],
      labels: ELEMENT_LABELS,
      pagination: {
        a: 0,
        b: DEFAULT_PAGINATION_LIMIT
      }
    }
  },
  computed: {
    filteredOptions: function () {
      return this.options.filter((option) => {
        return option.includes(this.searchPattern);
      });
    },
    loadMoreBtnVisibility: function () {
      return this.filteredOptions.length > this.pagination.b;
    },
    boxOptions: function () {
      return this.filteredOptions.slice(this.pagination.a, this.pagination.b);
    }
  },
  watch: {
    searchPattern: function () {
      this.pagination.b = DEFAULT_PAGINATION_LIMIT;
    }
  },
  created: function () {
    this.chosenOptions = [].concat(this.appliedOptions);
  },
  methods: {
    cutLongText (str) {
      return str.length > 14 ? `${str.substr(0, 14)}...` : str;
    },
    isSelected (option) {
      return this.chosenOptions.includes(option);
    },
    deselectAll () {
      this.chosenOptions = [];
    },
    selectAll () {
      this.chosenOptions = [].concat(this.options);
    },
    switchOption (option) {
      if (this.isSelected(option)) {
        this.chosenOptions = this.chosenOptions.filter((item) => {
          return item !== option;
        });
      } else {
        this.chosenOptions.push(option);
      }
    },
    onCloseAction () {
      const visibility = false;
      this.chosenOptions = [].concat(this.appliedOptions);
      this.onCloseClickHandler(this.columnName, visibility);
    },
    onApplyAction () {
      this.onApplyClickHandler(this.columnName, this.chosenOptions);
    },
    onLoadMoreAction () {
      this.pagination.b += 10;
    }
  }
}
</script>

<style scoped>
.filter-box {
  height: 415px;
  width: 280px;
  border: 1px solid rgba(0, 0, 0, 0.4);
  background-color: #ffffff;
  position: absolute;
  top: 60px;
  left: 0px;
}
#options {
  height: 180px;
  border: 1px solid rgba(0, 0, 0, 0.4);
  padding: 10px 10px 10px 10px;
  margin: 10px 10px 10px 10px;
}
.label-box {
  margin-left: 20px;
  margin-right: 20px;
  padding-top: 3px;
  min-width: 120px;
}
.pointer-btn {
  cursor: pointer;
}
#load-more {
  margin-top: 5px;
}
#load-more button {
  margin-left: 55px;
}
</style>
