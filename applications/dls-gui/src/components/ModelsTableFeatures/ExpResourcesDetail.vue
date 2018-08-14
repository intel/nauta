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
      <span>
        <b>{{ labels.PODS }} --</b>
      </span>
      <ol id="pods-list">
        <li v-bind:key="pod.name" v-for="pod in podsList">
          <b>{{ labels.NAME }}:</b> <i>{{ pod.name }}</i> <br/>
          <b>{{ labels.STATE }}:</b> <i>{{ pod.state }}</i> <br/>
          <b>{{ labels.CONTAINERS }}:</b>
          <ul id="containers-list">
            <li v-bind:key="container.name" v-for="container in pod.containers">
              <b>{{ labels.NAME }}:</b> <i>{{ container.name }}</i> <br/>
              <b>{{ labels.RESOURCES }}:</b> <i>{{ container.resources }}</i>
            </li>
          </ul>
        </li>
      </ol>
    </v-flex>
  </v-layout>
</template>

<script>
import ELEMENTS_LABELS from '../../utils/constants/labels';

export default {
  name: 'ExpResourcesDetail',
  data () {
    return {
      labels: ELEMENTS_LABELS
    }
  },
  props: ['keyname', 'podsList']
}
</script>

<style scoped>
#pods-list {
  margin-left: 25px;
}
#containers-list {
  margin-left: 25px;
}
.keyname {
  font-weight: bold;
}
.values {
  margin-left: 20px;
}
</style>
