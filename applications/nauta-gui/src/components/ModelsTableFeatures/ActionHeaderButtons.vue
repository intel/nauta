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
<div id="buttons_block">
  <v-btn dark small v-on:click="onLaunchTensorHandler()" :disabled="!tensorBtnAvailable">
    {{ labels.LAUNCH_TB }}*
  </v-btn>
  <v-menu bottom offset-y>
    <v-btn slot="activator" dark small>
      {{ labels.SORT_AND_FILTER }}
    </v-btn>
    <v-list>
      <v-list-tile v-on:click="switchAllUsersMode">
        <v-list-tile-title>{{ labels.ALL_USERS }}</v-list-tile-title>
        <v-list-tile-action v-if="allUsersMode" class="justify-end">
          <v-icon>done</v-icon>
        </v-list-tile-action>
      </v-list-tile>
      <v-list-tile v-on:click="clearSort()">
        <v-list-tile-title>{{ labels.CLEAR_SORT }}</v-list-tile-title>
      </v-list-tile>
      <v-list-tile v-on:click="clearFilterHandler()">
        <v-list-tile-title>{{ labels.CLEAR_FILTER }}</v-list-tile-title>
      </v-list-tile>
    </v-list>
  </v-menu>
  <v-menu bottom offset-y>
    <v-btn slot="activator" dark small>
      {{ labels.AUTO_REFRESH }}
    </v-btn>
    <v-list>
      <v-menu open-on-hover :close-on-content-click="false" offset-x>
        <v-list-tile slot="activator">
          <v-list-tile-title>{{ labels.SET_INTERVAL }}</v-list-tile-title>
          <v-list-tile-action class="justify-end">
            <v-icon>play_arrow</v-icon>
          </v-list-tile-action>
        </v-list-tile>
        <v-list dense>
          <v-list-tile :key="'interval-' + interval" v-for="interval in possibleRefreshIntervals" v-on:click="setRefreshIntervalValue(interval)">
            <v-list-tile-title>{{ interval }}s</v-list-tile-title>
            <v-list-tile-action v-if="refreshInterval === interval" class="justify-end">
              <v-icon>done</v-icon>
            </v-list-tile-action>
          </v-list-tile>
        </v-list>
      </v-menu>
      <v-list-tile v-on:click="refreshNowHandler()">
        <v-list-tile-title>{{ labels.REFRESH_NOW }}</v-list-tile-title>
      </v-list-tile>
    </v-list>
  </v-menu>
  <v-btn v-on:click="showColumnMgmtModalHandler()" dark small>
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
                <div id="options" v-if="isNonEmptyTable" class="scroll-y">
                  <div v-for="header in experimentsParams" v-bind:key="header" class="option">
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
                      <span slot="activator">
                        {{ cutLongText(getLabel(header), 20) }}
                      </span>
                      <span>{{ getLabel(header) }}</span>
                    </v-tooltip>
                  </div>
                </div>
                <div v-if="!isNonEmptyTable">
                  {{ messages.SUCCESS.NO_DATA_FOR_CURRENT_USER }}
                </div>
              </v-flex>
              <v-flex md8 xs12 offset-md2>
                <v-btn id="revert" v-if="isNonEmptyTable" block dark small v-on:click="revertToDefault()">
                  {{ labels.REVERT_TO_DEFAULT }}
                </v-btn>
              </v-flex>
              <v-flex md6 xs12>
                <v-btn color="intel_primary" block dark small v-on:click="discardVisibleHeaders()">
                  {{ isNonEmptyTable ? labels.CANCEL : labels.OK }}
                </v-btn>
              </v-flex>
              <v-flex v-if="isNonEmptyTable" md6 xs12>
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
import { mapGetters, mapActions } from 'vuex';
import HEADERS_LABELS from '../../utils/header-titles';
import ELEMENTS_LABELS from '../../utils/constants/labels';
import MESSAGES from '../../utils/constants/messages';
import { ALWAYS_VISIBLE_COLUMNS } from '../../store/modules/experiments-table';

export default {
  name: 'ActionHeaderButtons',
  props: ['clearSort', 'clearFilterHandler', 'onLaunchTensorHandler', 'refreshNowHandler'],
  data: () => {
    return {
      possibleRefreshIntervals: [5, 10, 15, 30, 60],
      showColumnMgmtModal: false,
      labels: ELEMENTS_LABELS,
      messages: MESSAGES,
      draft: []
    }
  },
  computed: {
    ...mapGetters({
      experimentsParams: 'experimentsParams',
      selectedExperimentsByUser: 'selectedExperimentsByUser',
      currentlyVisibleColumns: 'currentlyVisibleColumns',
      allUsersMode: 'allUsersMode',
      refreshInterval: 'refreshInterval'
    }),
    tensorBtnAvailable: function () {
      return this.selectedExperimentsByUser.length > 0;
    },
    isNonEmptyTable: function () {
      return this.experimentsParams.length > 0;
    }
  },
  created: function () {
    this.draft = [].concat(this.currentlyVisibleColumns);
  },
  methods: {
    ...mapActions({
      showColumns: 'showColumns',
      clearColumnsSelection: 'clearColumnsSelection',
      switchAllUsersMode: 'switchAllUsersMode',
      updateRefreshInterval: 'updateRefreshInterval'
    }),
    getLabel: function (header) {
      return HEADERS_LABELS[header] || header.charAt(0).toUpperCase() + header.slice(1);
    },
    cutLongText (str, limit) {
      return str.length > limit ? `${str.substr(0, limit)}...` : str;
    },
    revertToDefault: function () {
      this.clearColumnsSelection();
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
      return ALWAYS_VISIBLE_COLUMNS.includes(name);
    },
    applyVisibleHeaders: function () {
      this.showColumns({ data: this.draft });
      this.showColumnMgmtModal = false;
    },
    discardVisibleHeaders: function () {
      this.draft = [].concat(this.currentlyVisibleColumns);
      this.showColumnMgmtModal = false;
    },
    setRefreshIntervalValue: function (value) {
      this.updateRefreshInterval({data: value});
    },
    showColumnMgmtModalHandler: function () {
      this.showColumnMgmtModal = !this.showColumnMgmtModal;
    }
  }
}
</script>

<style scoped>
#buttons_block button {
  margin-top: 22px;
  color: rgb(0, 113, 197);
  background-color: rgba(0, 113, 197, 0.12);
  width: 160px;
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
