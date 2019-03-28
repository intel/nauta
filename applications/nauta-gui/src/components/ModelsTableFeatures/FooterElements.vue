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
<div class="datatable table">
  <div class="datatable__actions">
    <div class="refreshStat">
      {{ refreshMessage }}
    </div>
    <v-spacer></v-spacer>
    {{ labels.ROWS_PER_PAGE }}:
    <div class="datatable__actions__select">
      <v-select
        :items="itemsPerPageOptions"
        v-model="chosenCount"
        single-line
      ></v-select>
    </div>
    <div class="datatable__actions__range-controls">
      <div class="datatable__actions__pagination">
        {{ paginationStats }}
      </div>
      <v-btn flat v-on:click="previousPage()" :disabled="currentPage == 1">
        <v-icon>keyboard_arrow_left</v-icon>
      </v-btn>
      <input
        id="setPageInput"
        type="number"
        v-model="chosenPageNo"
        v-on:blur="onPageNoInputChange"
      />
      <v-btn flat v-on:click="nextPage()" :disabled="currentPage == pagesCount">
        <v-icon>keyboard_arrow_right</v-icon>
      </v-btn>
    </div>
  </div>
</div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';
import ELEMENT_LABELS from '../../utils/constants/labels';

export default {
  name: 'FooterElements',
  data: () => {
    return {
      labels: ELEMENT_LABELS,
      itemsPerPageOptions: [5, 10, 15, 25],
      chosenCount: 5
    }
  },
  computed: {
    ...mapGetters({
      pagesCount: 'experimentsTotalPagesCount',
      experimentsBegin: 'experimentsBegin',
      experimentsEnd: 'experimentsEnd',
      filteredDataCount: 'filteredDataCount',
      itemsCountPerPage: 'itemsCountPerPage',
      currentPage: 'currentPage',
      experimentsPageNumber: 'experimentsPageNumber',
      refreshMessage: 'refreshMessage'
    }),
    chosenPageNo: {
      get: function () {
        return this.currentPage;
      },
      set: function (val) {
        return val;
      }
    },
    paginationStats: function () {
      return `${this.experimentsBegin}-${this.experimentsEnd} ${this.labels.OF} ${this.filteredDataCount}`;
    }
  },
  watch: {
    chosenCount: function (val) {
      this.updateCountPerPage(val);
    },
    experimentsPageNumber: function () {
      this.updatePageNumber({data: this.experimentsPageNumber});
    }
  },
  methods: {
    ...mapActions([
      'updatePageNumber',
      'updateItemsCountPerPage'
    ]),
    updateCountPerPage (count) {
      this.updatePageNumber({data: 1});
      this.updateItemsCountPerPage({data: count});
    },
    nextPage () {
      this.updatePageNumber({data: this.currentPage + 1});
    },
    setPage (pageNumber) {
      this.updatePageNumber({data: pageNumber});
    },
    previousPage () {
      this.updatePageNumber({data: this.currentPage - 1});
    },
    onPageNoInputChange: function (e) {
      const requiredPage = e.target.value;
      if (requiredPage >= 1) {
        this.setPage(requiredPage);
      } else {
        this.setPage(1);
        this.chosenPageNo = 1;
      }
    }
  }
}
</script>

<style scoped>
.refreshStat {
  margin-left: 25px;
}
.datatable__actions__select {
  margin-top: 18px;
}
#setPageInput input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
#setPageInput input[type="number"] {
  -moz-appearance: textfield;
}
input {
  text-align: center;
}
</style>
