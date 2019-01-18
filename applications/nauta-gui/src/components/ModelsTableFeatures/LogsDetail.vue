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
  <v-layout>
    <v-flex xs3>
      <span class="keyname">{{ keyname }}:</span>
    </v-flex>
    <v-flex xs9 class="values">
      <div class="row">
        <span class="kind">
          {{ `${labels.LOGS}, ${labels.ALL}` }}
        </span>
        <span class="links">
          <a :href="`/api/experiments/${name}/${owner}/logs/download`" :download="`${name}.txt`">{{ labels.DOWNLOAD }}</a>
        </span>
      </div>
      <div class="row">
        <span class="kind">
          {{ `${labels.LOGS}, ${labels.LAST} 100` }}
        </span>
        <span class="links">
          <a :href="`/api/experiments/${name}/${owner}/logs/last/show/100`" target="_blank">{{ labels.VIEW }}</a>
        </span>
      </div>
    </v-flex>
  </v-layout>
</template>

<script>
import ELEMENTS_LABELS from '../../utils/constants/labels';

export default {
  name: 'LogsDetail',
  data () {
    return {
      labels: ELEMENTS_LABELS
    }
  },
  props: ['keyname', 'name', 'owner']
}
</script>

<style scoped>
#pods-list {
  margin-left: 25px;
  font-size: 12px;
}
#containers-list {
  margin-left: 25px;
}
.keyname {
  font-weight: bold;
  font-size: 12px;
}
.values {
  margin-left: 20px;
  font-size: 12px;
}
.kind {
  margin-right: 30px;
  width: 100px;
  float: left;
}
</style>
