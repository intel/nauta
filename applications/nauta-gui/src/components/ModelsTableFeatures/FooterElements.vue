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
      {{ lastUpdateLabel }}
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
      <v-btn flat v-on:click="prevPageAction()" :disabled="currentPage == 1">
        <v-icon>keyboard_arrow_left</v-icon>
      </v-btn>
      <v-btn flat v-on:click="nextPageAction()" :disabled="currentPage == pagesCount">
        <v-icon>keyboard_arrow_right</v-icon>
      </v-btn>
    </div>
  </div>
</div>
</template>

<script>
import ELEMENT_LABELS from '../../utils/constants/labels';

export default {
  name: 'FooterElements',
  props: ['updateCountHandler', 'currentPage', 'pagesCount', 'nextPageAction', 'prevPageAction', 'paginationStats',
    'lastUpdateLabel'],
  data: () => {
    return {
      labels: ELEMENT_LABELS,
      itemsPerPageOptions: [5, 10, 15, 25],
      chosenCount: 5
    }
  },
  watch: {
    chosenCount: function (val) {
      this.updateCountHandler(val);
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
</style>
