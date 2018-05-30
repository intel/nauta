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
      <v-list-tile>
        <v-list-tile-title>Clear filter</v-list-tile-title>
      </v-list-tile>
      <v-list-tile>
        <v-list-tile-title>Revert models to original order</v-list-tile-title>
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
        <v-layout row wrap>
          <v-flex xs12>
            <div v-for="header in headers" v-bind:key="header" class="input-group input-group--dirty checkbox input-group--selection-controls input-group--active accent--text">
              <label :for="header">{{ header }}</label>
              <div class="input-group__input">
                <input :id="header" type="checkbox" v-model="visibilityDraft[header]"/>
              </div>
            </div>
          </v-flex>
          <v-flex md6 offset-md-3 xs6 offset-xs3>
            <v-btn block color="intel_primary" dark small v-on:click="revertToDefault()">REVERT TO DEFAULT</v-btn>
          </v-flex>
          <v-flex xs5 v-on:click="showColumnMgmtModal = false">
            <v-btn block color="intel_primary" dark small>CANCEL</v-btn>
          </v-flex>
          <v-spacer></v-spacer>
          <v-flex xs5>
            <v-btn block color="intel_primary" dark small v-on:click="applyHiddenHeaders()">APPLY</v-btn>
          </v-flex>
        </v-layout>
      </v-card-text>
    </v-card>
  </v-dialog>
</div>
</template>

<script>
import {mapGetters} from 'vuex';
import lodash from 'lodash';

export default {
  name: 'ActionHeaderButtons',
  props: ['clearSort', 'setHiddenColumnsHandler', 'hiddenColumns', 'headers', 'onLaunchTensorHandler',
    'onDiscardTensorHandler', 'disabled'],
  data: () => {
    return {
      showColumnMgmtModal: false,
      visibilityDraft: {}
    }
  },
  watch: {
    hiddenColumns: function () {
      this.headers.forEach((header) => {
        this.visibilityDraft[header] = this.hiddenColumns.indexOf(header) === -1;
      });
    },
    headers: function () {
      this.headers.forEach((header) => {
        this.visibilityDraft[header] = this.hiddenColumns.indexOf(header) === -1;
      });
    }
  },
  computed: {
    ...mapGetters({
      tensorModeViewState: 'tensorMode'
    })
  },
  methods: {
    revertToDefault: function () {
      this.setHiddenColumnsHandler([]);
      this.showColumnMgmtModal = false;
    },
    applyHiddenHeaders: function () {
      const filteredColumns = lodash.mapKeys(this.visibilityDraft, (value, key) => {
        if (!value) {
          return key;
        }
      });
      const filteredColumnsNames = lodash.keys(filteredColumns);
      this.setHiddenColumnsHandler(filteredColumnsNames);
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
input {
  margin: 7px;
}
</style>
