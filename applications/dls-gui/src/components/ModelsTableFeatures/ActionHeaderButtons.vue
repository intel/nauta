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
  <v-btn dark small v-on:click="onLaunchTensorHandler()">LAUNCH TENSORBOARD</v-btn>
  <v-btn v-if="tensorModeViewState" dark small v-on:click="onDiscardTensorHandler()">EXIT</v-btn>
  <v-menu v-if="!tensorModeViewState" bottom offset-y>
    <v-btn slot="activator" dark small>RESET</v-btn>
    <v-list>
      <v-list-tile v-on:click="clearSort()">
        <v-list-tile-title>Clear sort</v-list-tile-title>
      </v-list-tile>
      <v-list-tile v-on:click="clearFilterHandler()">
        <v-list-tile-title>Clear filter</v-list-tile-title>
      </v-list-tile>
    </v-list>
  </v-menu>
  <v-btn v-if="!tensorModeViewState" v-on:click="showColumnMgmtModal = !showColumnMgmtModal" dark small>ADD/DELETE COLUMNS</v-btn>
  <v-dialog
    v-model="showColumnMgmtModal"
    max-width="600px"
  >
      <v-card>
        <v-card-title>
          <h2>Add/Delete Columns</h2>
        </v-card-title>
        <v-card-text>
          <v-container grid-list-md>
            <v-layout row wrap>
              <v-flex xs12>
                <div id="options" class="scroll-y">
                  <div v-for="header in switchableColumns" v-bind:key="header" class="input-group input-group--selection-controls">
                    <v-icon :id="header + '_on'" class="pointer-btn" :color="isHidden(header) ? 'grey lighten-3' : 'success'" v-on:click="showColumn(header)">done</v-icon>
                    <span class="label-box" v-on:click="showColumn(header)">{{ getLabel(header) }}</span>
                    <v-icon :id="header + '_off'" class="pointer-btn" :color="isHidden(header) ? 'grey lighten-3' : 'grey darken-2'" v-on:click="hideColumn(header)">delete</v-icon>
                  </div>
                </div>
              </v-flex>
              <v-flex md4 xs12 offset-md4>
                <v-btn id="revert" block dark small v-on:click="revertToDefault()">REVERT TO DEFAULT</v-btn>
              </v-flex>
              <v-flex md6 xs12>
                <v-btn color="intel_primary" block dark small v-on:click="discardHiddenHeaders()">CANCEL</v-btn>
              </v-flex>
              <v-flex md6 xs12>
                <v-btn color="intel_primary" block dark small v-on:click="applyHiddenHeaders()">SAVE</v-btn>
              </v-flex>
            </v-layout>
          </v-container>
        </v-card-text>
      </v-card>
  </v-dialog>
</div>
</template>

<script>
import {mapGetters} from 'vuex';
import LABELS from '../../utils/header-titles';

export default {
  name: 'ActionHeaderButtons',
  props: ['clearSort', 'clearFilterHandler', 'setHiddenColumnsHandler', 'hiddenColumns', 'alwaysVisibleColumns', 'headers',
    'onLaunchTensorHandler', 'onDiscardTensorHandler', 'disabled'],
  data: () => {
    return {
      showColumnMgmtModal: false,
      draft: []
    }
  },
  watch: {
    hiddenColumns: function () {
      this.draft = [].concat(this.hiddenColumns)
    }
  },
  computed: {
    ...mapGetters({
      tensorModeViewState: 'tensorMode'
    }),
    switchableColumns: function () {
      const options = this.headers.filter((header) => {
        return !this.alwaysVisibleColumns.includes(header);
      });
      return Array.from(new Set(this.draft.concat(options))).reverse();
    },
    initialHiddenHeaders: function () {
      return this.headers.filter((header) => {
        return !this.alwaysVisibleColumns.includes(header);
      });
    }
  },
  created: function () {
    this.setHiddenColumnsHandler(this.initialHiddenHeaders)
  },
  methods: {
    getLabel: function (header) {
      return LABELS[header] || header;
    },
    revertToDefault: function () {
      this.setHiddenColumnsHandler(this.initialHiddenHeaders);
      this.showColumnMgmtModal = false;
    },
    hideColumn: function (name) {
      this.draft.push(name);
    },
    showColumn: function (name) {
      this.draft = this.draft.filter((column) => {
        return column !== name;
      });
    },
    isHidden: function (name) {
      return this.draft.includes(name);
    },
    applyHiddenHeaders: function () {
      this.setHiddenColumnsHandler(this.draft);
      this.showColumnMgmtModal = false;
    },
    discardHiddenHeaders: function () {
      this.draft = [].concat(this.hiddenColumns);
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
