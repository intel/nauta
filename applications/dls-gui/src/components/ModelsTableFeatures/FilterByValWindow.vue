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
      <h4>Filter by values...</h4>
      <v-layout row wrap>
        <v-flex xs12>
          <v-btn color="intel_primary" small flat v-on:click="selectAll()">Select All</v-btn>
          <v-btn color="intel_primary" small flat v-on:click="deselectAll()">Clear All</v-btn>
        </v-flex>
        <v-flex xs12>
          <v-text-field v-model="searchPattern" append-icon="search" box hide-details></v-text-field>
        </v-flex>
        <v-flex xs12>
          <div id="options" class="scroll-y">
            <div v-for="option in boxOptions" v-bind:key="option"
                 class="input-group--selection-controls" v-on:click="switchOption(option)">
              <v-icon :id="option" class="pointer-btn" :color="isSelected(option) ? 'success' : 'grey lighten-3'">done</v-icon>
              <v-tooltip bottom>
                <span slot="activator" class="label-box">
                  {{ cutLongText(option) }}
                </span>
                <span>{{ option }}</span>
              </v-tooltip>
            </div>
          </div>
        </v-flex>
        <v-flex xs12 pl-3>
          <v-btn dark small color="intel_primary" v-on:click="onCloseAction()">CANCEL</v-btn>
          <v-btn dark small color="intel_primary" v-on:click="onApplyAction()">OK</v-btn>
        </v-flex>
      </v-layout>
    </v-container>
  </div>
</template>

<script>

export default {
  name: 'FilterByValWindow',
  props: ['columnName', 'options', 'appliedOptions', 'onCloseClickHandler', 'onApplyClickHandler'],
  data: () => {
    return {
      searchPattern: '',
      chosenOptions: []
    }
  },
  computed: {
    boxOptions: function () {
      return this.options.filter((option) => {
        return option.includes(this.searchPattern);
      })
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
  z-index: 10;
  position: absolute;
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
</style>
