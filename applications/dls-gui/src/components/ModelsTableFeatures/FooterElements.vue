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
<div class="datatable table">
  <div class="datatable__actions">
    <div class="refreshStat">
      {{ lastUpdateLabel }}
    </div>
    <v-spacer></v-spacer>
    Rows per page:
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
export default {
  name: 'FooterElements',
  props: ['updateCountHandler', 'currentPage', 'pagesCount', 'nextPageAction', 'prevPageAction', 'paginationStats',
    'lastUpdateLabel'],
  data: () => {
    return {
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
