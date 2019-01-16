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
