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
<div id="buttons_block">
  <v-btn dark small v-on:click="onLaunchTensorHandler()" :disabled="launchTensorDisabled">
    {{ labels.LAUNCH_TB }}*
  </v-btn>
  <v-menu bottom offset-y>
    <v-btn slot="activator" dark small>
      {{ labels.RESET }}
    </v-btn>
    <v-list>
      <v-list-tile v-on:click="clearSort()">
        <v-list-tile-title>{{ labels.CLEAR_SORT }}</v-list-tile-title>
      </v-list-tile>
      <v-list-tile v-on:click="clearFilterHandler()">
        <v-list-tile-title>{{ labels.CLEAR_FILTER }}</v-list-tile-title>
      </v-list-tile>
    </v-list>
  </v-menu>
  <v-btn v-on:click="showColumnMgmtModal = !showColumnMgmtModal" dark small>
    {{ labels.ADD_DEL_COLUMN }}
  </v-btn>
  <v-dialog
    v-model="showColumnMgmtModal"
    max-width="295px"
  >
      <v-card>
        <v-card-title>
          <h2>
            {{ labels.ADD_DEL_COLUMN }}
          </h2>
        </v-card-title>
        <v-card-text>
          <v-container grid-list-md>
            <v-layout row wrap>
              <v-flex xs12>
                <div id="options" class="scroll-y">
                  <div v-for="header in columns" v-bind:key="header" class="option">
                    <v-icon
                      :id="header + '_switch'"
                      v-if="!isHidden(header)"
                      color="success"
                      v-on:click="switchColumn(header)"
                      class="pointer-btn"
                      :disabled="isAlwaysVisible(header)">
                      check_circle
                    </v-icon>
                    <v-icon
                      :id="header + '_switch'"
                      v-if="isHidden(header)"
                      v-on:click="switchColumn(header)"
                      class="pointer-btn">
                      panorama_fish_eye
                    </v-icon>
                    <v-tooltip bottom class="label-box">
                      <span slot="activator" v-on:click="showColumn(header)">
                        {{ cutLongText(getLabel(header), 20) }}
                      </span>
                      <span>{{ getLabel(header) }}</span>
                    </v-tooltip>
                  </div>
                </div>
              </v-flex>
              <v-flex md8 xs12 offset-md2>
                <v-btn id="revert" block dark small v-on:click="revertToDefault()">
                  {{ labels.REVERT_TO_DEFAULT }}
                </v-btn>
              </v-flex>
              <v-flex md6 xs12>
                <v-btn color="intel_primary" block dark small v-on:click="discardVisibleHeaders()">
                  {{ labels.CANCEL }}
                </v-btn>
              </v-flex>
              <v-flex md6 xs12>
                <v-btn color="intel_primary" block dark small v-on:click="applyVisibleHeaders()">
                  {{ labels.SAVE }}
                </v-btn>
              </v-flex>
            </v-layout>
          </v-container>
        </v-card-text>
      </v-card>
  </v-dialog>
</div>
</template>

<script>
import HEADERS_LABELS from '../../utils/header-titles';
import ELEMENTS_LABELS from '../../utils/constants/labels';

export default {
  name: 'ActionHeaderButtons',
  props: ['clearSort', 'clearFilterHandler', 'setVisibleColumnsHandler', 'selectedByUserColumns',
    'columns', 'alwaysVisibleColumns', 'initiallyVisibleColumns', 'onLaunchTensorHandler',
    'launchTensorDisabled', 'disabled'],
  data: () => {
    return {
      showColumnMgmtModal: false,
      draft: [],
      labels: ELEMENTS_LABELS
    }
  },
  watch: {
    selectedByUserColumns: function () {
      this.draft = [].concat(this.selectedByUserColumns)
    }
  },
  created: function () {
    this.setVisibleColumnsHandler(this.selectedByUserColumns.concat(this.initiallyVisibleColumns))
  },
  methods: {
    getLabel: function (header) {
      return HEADERS_LABELS[header] || header.charAt(0).toUpperCase() + header.slice(1);
    },
    cutLongText (str, limit) {
      return str.length > limit ? `${str.substr(0, limit)}...` : str;
    },
    revertToDefault: function () {
      this.draft = this.initiallyVisibleColumns;
      this.setVisibleColumnsHandler(this.draft);
      this.showColumnMgmtModal = false;
    },
    switchColumn: function (name) {
      if (this.draft.includes(name)) {
        this.draft = this.draft.filter((item) => {
          return item !== name;
        });
      } else {
        this.draft.push(name);
      }
    },
    isHidden: function (name) {
      return !this.draft.includes(name);
    },
    isAlwaysVisible: function (name) {
      return this.alwaysVisibleColumns.includes(name);
    },
    applyVisibleHeaders: function () {
      this.setVisibleColumnsHandler(this.draft);
      this.showColumnMgmtModal = false;
    },
    discardVisibleHeaders: function () {
      this.draft = [].concat(this.selectedByUserColumns);
      this.showColumnMgmtModal = false;
    }
  }
}
</script>

<style scoped>
#buttons_block button {
  margin-top: 22px;
  color: rgb(0, 113, 197);
  background-color: rgba(0, 113, 197, 0.12);
  width: 170px;
}
#buttons_block button:disabled {
  color: rgb(255, 255, 255) !important;
  background-color: rgba(0, 113, 197, 0.12) !important;
}
#revert {
  color: rgb(0, 113, 197);
  background-color: rgba(0, 113, 197, 0.12);
}
input {
  margin: 7px;
}
#options {
  max-height: 180px;
  border: 1px solid #000000;
  padding: 10px 10px 10px 10px;
}
.option {
  white-space: nowrap;
  display: flex;
}
.label-box {
  margin-left: 20px;
  margin-right: 20px;
  padding-top: 3px;
  min-width: 150px;
  cursor: help;
}
.pointer-btn {
  cursor: pointer;
}
</style>
